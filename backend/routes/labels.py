from typing import List

from fastapi import HTTPException, APIRouter, Depends
from starlette import status

from ..config import db
from ..models import Label, CreateLabelDTO, LabelDTO, User
from ..utils import get_current_active_user

label_router = APIRouter()


@label_router.get("/", response_model=List[LabelDTO])
async def get_labels(dataset_id: int, current_user: User = Depends(get_current_active_user)):
    """
    This function responds to a request for /api/int:dataset_id/labels
    with the complete lists of data sets

    :return:        json string of list of labels for a data set
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You may not be logged in or your account is deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    labels = db.query(Label).filter(Label.dataset_id == dataset_id)

    if labels is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Labels not found for data set: {}".format(dataset_id),
        )

    return list(labels)


@label_router.post("/", response_model=LabelDTO)
async def post_labels(dataset_id: int, label: CreateLabelDTO, current_user: User = Depends(get_current_active_user)):
    """ Create a new label for the given dataset. """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You may not be logged in or your account is deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_label = Label(name=label.name, dataset_id=dataset_id)
    db.add(new_label)
    db.commit()

    return new_label
