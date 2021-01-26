from sqlalchemy.exc import IntegrityError

from fastapi import status, APIRouter, HTTPException, Depends

from ..worker import manager
from ..config import db
from ..models import Sample, SampleDTO, User, UnlabelDTO, Label, Association, Dataset
from ..utils import get_current_user, can_assign, get_current_active_user

sample_router = APIRouter()


@sample_router.get("/{sample_id}", response_model=SampleDTO)
def get_sample(sample_id: int):
    sample = db.query(Sample).filter_by(id=sample_id).first()
    if sample is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found for id: {}.".format(sample_id),
        )

    sample.ensure_string_content()
    return sample


@sample_router.post("/{sample_id}", response_model=SampleDTO)
def post_sample(sample_id: int, label_id: int, user: User = Depends(get_current_user)):
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
        # TODO: Investigate how this can be done using a method other than a raw query
        # It seems like SQLAlchemy tries to load the sample and then tries to save it again
        # However, while loading it converts the content of the sample to text and fails to save it again
        # because it expects a byte-like object.

        # new_association = Association(
        #     sample_id=sample_id, label_id=label_id, user_id=user.id
        # )
        # db.add(new_association)
        # db.commit()
        db.execute(f'INSERT INTO association (sample_id, label_id, user_id) VALUES ({sample_id}, {label_id}, {user.id})')
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    # Retrieve pipe endpoint for process with corresponding dataset_id and send new label
    dataset = db.query(Sample).get(sample_id).dataset

    worker = manager.get_or_else_load(dataset)
    worker.add_sample_label(sample_id=sample_id, label_id=label_id)

    next_sample = worker.get_next_sample()
    if not next_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the next sample.",
        )
    next_sample.ensure_string_content()
    return next_sample


@sample_router.delete("/{sample_id}", response_model=int)
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

    label = db.query(Label).filter(Label.id == data.label_id).first()
    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No label {data.label_id}'
        )

    associations = db.query(Association).filter(Association.sample_id == sample_id, Association.label_id == data.label_id)

    if not data.all:
        associations = associations.filter(Association.user_id == user.id)

    worker = manager.get_or_else_load(sample.dataset)
    worker.remove_sample_label(sample_id=sample_id, label_id=data.label_id)

    return associations.delete()




