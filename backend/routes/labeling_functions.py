import re
from typing import List
from traceback import format_exc

from fastapi import APIRouter, HTTPException, status

from ..config import db
from ..models import LabelingFunction, LabelingFunctionDTO, SampleDTO, Sample, TestRunResponse, LabelDTO
from sqlalchemy.sql.expression import func

labeling_functions_router = APIRouter()


@labeling_functions_router.get("/", response_model=List[LabelingFunctionDTO])
async def get_dataset_labeling_functions(dataset_id: int):
    """Return the functions used for automatic labeling for the given dataset."""

    labeling_functions = db.query(LabelingFunction).filter(LabelingFunction.dataset_id == dataset_id).all()

    if labeling_functions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No labeling-functions found for data-set: {}.".format(dataset_id)
        )
    return labeling_functions


@labeling_functions_router.post("/")
async def post_dataset_labeling_functions(dataset_id: int, labeling_functions_dto: List[LabelingFunctionDTO]):
    """Update or insert labeling-functions for the given dataset."""

    # compare old functions and delete
    new_functions = {lf.id: lf for lf in labeling_functions_dto}
    existing_functions: List[LabelingFunction] = db.query(LabelingFunction).filter(
        LabelingFunction.dataset_id == dataset_id).all()
    for existing_lf in existing_functions:
        if existing_lf.id in new_functions:
            new_lf: LabelingFunctionDTO = new_functions.get(existing_lf.id)
            if existing_lf.function_body != new_lf.function_body:
                existing_lf.function_body = new_lf.function_body
            new_functions.pop(existing_lf.id)
        else:
            db.delete(existing_lf)

    # add new
    for new_lf in new_functions.values():
        lf = LabelingFunction(function_body=new_lf.function_body, dataset_id=dataset_id)
        db.add(lf)
    db.commit()


@labeling_functions_router.post("/testrun/", response_model=TestRunResponse)
async def test_run(dataset_id: int, labeling_functions_dto: List[LabelingFunctionDTO]):
    """Run given labeling-functions on a random sample."""

    # get random sample
    sample: SampleDTO = db.query(Sample).filter_by(dataset_id = dataset_id).order_by(func.random()).limit(5).first()
    if sample is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sample found for data-set: {}.".format(dataset_id)
        )
    # execute functions on sample
    results: List[str] = []
    for labeling_function in labeling_functions_dto:
        # try to find a function definition
        function_name = re.search(r"def(.+)\(", labeling_function.function_body)
        if function_name is None:
            results.append("No function definition found.")
            continue
        function_name = function_name.group(1).strip()
        function_call = labeling_function.function_body + f"\nlabel.append({function_name}(sample))"
        try:
            label= [] # using list as container with clear reference (preventing multi-assignment)
            exec(function_call,{"sample":sample}, {"label": label})
            if len(label) > 0 and label[0] is not None:
                if isinstance(label[0], LabelDTO):
                    results.append(label[0].name)
                else:
                    results.append(label[0])
            else:
                results.append("No result")
        except Exception as e:
            results.append(str(e))

    return TestRunResponse(result=results, sample=sample)
