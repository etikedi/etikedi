from sqlalchemy.exc import IntegrityError

from fastapi import status, APIRouter, HTTPException, Depends

from ..worker import get_next_sample, notify_about_new_sample
from ..config import db
from ..models import Association, Sample, SampleDTO, User
from ..utils import get_current_user, can_assign

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

    notify_about_new_sample(
        dataset=dataset, user_id=user.id, sample_id=sample_id, label_id=label_id
    )

    next_sample = get_next_sample(dataset)
    if not next_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the next sample.",
        )
    next_sample.ensure_string_content()
    return next_sample
