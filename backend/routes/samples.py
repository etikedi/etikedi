from fastapi import status, APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError

from ..config import db, SQLAlchemyError
from ..models import Sample, SampleDTO, User, UnlabelDTO, Label, Association, Dataset
from ..utils import can_assign, get_current_active_user, get_current_active_admin
from ..worker import manager

sample_router = APIRouter()


@sample_router.get("/{sample_id}", response_model=SampleDTO)
def get_sample(sample_id: int, user: User = Depends(get_current_active_user)):
    sample = db.query(Sample).filter_by(id=sample_id).first()
    if sample is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found for id: {}.".format(sample_id),
        )

    return sample


@sample_router.post("/{sample_id}", response_model=SampleDTO)
def post_sample(sample_id: int, label_id: int, user: User = Depends(get_current_active_user)):
    """
    Associate a sample with a label and return the next label.

    :param sample_id:   ID of data sample to find
    :param label_id:    ID of the label
    :param user:        Current user Object
    :return:            data set matching ID
    """
    if not can_assign(sample_id, label_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't assign label to sample.",
        )

    try:
        new_association = Association(
             sample_id=sample_id, label_id=label_id, user_id=user.id
        )
        db.add(new_association)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    # Retrieve pipe endpoint for process with corresponding dataset_id and send new label
    dataset = db.query(Sample).get(sample_id).dataset

    worker = manager.get_or_else_load(dataset)
    worker.add_sample_label(sample_id=sample_id)

    next_sample_id = worker.get_next_sample_id()
    next_sample = db.get(Sample, next_sample_id)
    if not next_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the next sample.",
        )
    return next_sample


@sample_router.delete("/{sample_id}", response_model=None)
def unlabel(sample_id: int, data: UnlabelDTO, user=Depends(get_current_active_user)):
    if 'admin' not in user.roles and data.all:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only admin users are allowed to remove associations of other users'
        )

    sample = db.query(Sample).join(Dataset).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No sample {sample_id}'
        )

    associations = db.query(Association).filter(Association.sample_id == sample_id)
    label_ids = set()

    if not data.label_id:
        if not data.all:
            # error, needs at least label_id or all = True to delete something
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cannot remove association if label_id or all is not set.'
            )
    else:
        label = db.query(Label).filter(Label.id == data.label_id).first()
        if not label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'No label {data.label_id}'
            )
        label_ids.add(data.label_id)
        associations = associations.filter(Association.label_id == data.label_id)
        if not data.all:
            associations = associations.filter(Association.user_id == user.id)

    associations = associations.all()

    # deactivate all associations
    for association in associations:
        association.is_current = False
        if association.label_id not in label_ids:
            label_ids.add(association.label_id)

    db.commit()

    # remove association from AL
    worker = manager.get_or_else_load(sample.dataset)
    for _ in label_ids:
        worker.remove_sample_label(sample_id=sample_id)