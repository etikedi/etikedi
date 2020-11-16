from sqlite3 import IntegrityError

from fastapi import Depends, status, APIRouter, HTTPException
from sqlalchemy.orm import Session

from ..active_learning_process import get_next_sample, notify_about_new_sample
from ..config import get_db
from ..models import Association, Sample, SampleDTO
from ..utils import get_current_active_user, can_assign

sample_router = APIRouter()


@sample_router.get("/{sample_id}", response_model=SampleDTO)
def get_sample(sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter_by(id=sample_id).first()
    if sample is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found for id: {}.".format(sample_id)
        )

    return sample


@sample_router.post("/{sample_id}", response_model=SampleDTO)
def post_sample(sample_id: int, label_id: int, db: Session = Depends(get_db)):
    """
    Associate a sample with a label and return the next label.

    :param sample_id:   ID of data sample to find
    :param label_id:    ID of the label
    :param db:          Database connection
    :return:            data set matching ID
    """
    user = get_current_active_user()

    if not can_assign(sample_id, label_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't assign label to sample."
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

    notify_about_new_sample(
        dataset=dataset, user_id=user.id, sample_id=sample_id, label_id=label_id
    )

    next_sample = get_next_sample(dataset)
    if not next_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the next sample."
        )
    next_sample.ensure_string_content()
    return next_sample
