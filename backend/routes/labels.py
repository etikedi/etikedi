from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from ..config import get_db
from ..models import Label

label_router = APIRouter()


@label_router.get("/datasets/{dataset_id}/labels")
async def get_labels(dataset_id: int, db: Session = Depends(get_db)):
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

    return labels
    # return LabelSchema(many=True).dump(labels)


@label_router.post("/datasets/{dataset_id}/labels")
async def post_labels(dataset_id: int):
    """ TODO: Allow adding labels for admins """
    pass
