from typing import List

from fastapi import APIRouter, HTTPException, status

from ..config import db
from ..models import LabelingFunction, LabelingFunctionDTO

labeling_functions_router = APIRouter()


@labeling_functions_router.get("/", response_model=List[LabelingFunctionDTO])
async def get_dataset_labeling_functions(dataset_id: int):
    """Return the functions used for automatic labeling for the given dataset"""

    labeling_functions = db.query(LabelingFunction).filter(LabelingFunction.dataset_id == dataset_id).all()

    if labeling_functions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No labeling-functions found for data-set: {}.".format(dataset_id)
        )
    return labeling_functions


@labeling_functions_router.post("/")
async def post_dataset_labeling_functions(dataset_id: int, labeling_functions_dto: List[LabelingFunctionDTO]):
    """Update or insert labeling-functions for the given dataset"""
    new_labeling_function_list: List[LabelingFunction] = \
        [LabelingFunction(function_body=func.function_body, dataset_id=dataset_id)
         for func in labeling_functions_dto]
    # remove old
    for labeling_func in db.query(LabelingFunction).filter(LabelingFunction.dataset_id == dataset_id).all():
        db.delete(labeling_func)
    # add new
    for new_labeling_func in new_labeling_function_list:
        db.add(new_labeling_func)
    db.commit()
