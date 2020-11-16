from typing import List

from fastapi import HTTPException, APIRouter
from starlette import status

from ..config import db
from ..models import Label, CreateLabelDTO, LabelDTO

label_router = APIRouter()


@label_router.get("/", response_model=List[LabelDTO])
async def get_labels(dataset_id: int):
    """
    This function responds to a request for /api/int:dataset_id/labels
    with the complete lists of data sets

    :return:        json string of list of labels for a data set
    """
    labels = db.query(Label).filter(Label.dataset_id == dataset_id)

    if labels is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Labels not found for data set: {}".format(dataset_id)
        )

    return list(labels)


@label_router.post("/", response_model=LabelDTO)
async def post_labels(dataset_id: int, label: CreateLabelDTO):
    """ Create a new label for the given dataset. """
    new_label = Label(
        name=label.name,
        dataset_id=dataset_id
    )
    db.add(new_label)
    db.commit()

    return new_label
