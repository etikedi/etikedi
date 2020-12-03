from typing import List

from fastapi import Depends, UploadFile, File, Form, HTTPException, APIRouter, status

from ..worker import get_next_sample
from ..config import db
from ..importing import import_dataset
from ..models import Dataset, DatasetDTO, User, Table, Image, Text, SampleDTO
from ..utils import get_current_active_user

dataset_router = APIRouter()


@dataset_router.get("", response_model=List[DatasetDTO])
def get_datasets():
    datasets = db.query(Dataset).all()
    return datasets


@dataset_router.post("", response_model=DatasetDTO)
def create_dataset(
    name: str = Form(...),
    sample_type: str = Form(...),
    features: UploadFile = File(...),
    contents: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    sample_class = {"table": Table, "image": Image, "text": Text}[sample_type]
    if not sample_class:
        raise HTTPException(status_code=400, detail="Not a valid sample type")

    dataset, number_of_samples = import_dataset(
        name=name,
        sample_class=sample_class,
        features=features.file,
        content=contents.file,
        user=current_user,
        ensure_incomplete=True,
    )

    return dataset


@dataset_router.get("/{dataset_id}/first_sample", response_model=SampleDTO)
def get_first_sample(dataset_id: int):
    dataset = db.query(Dataset).get(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found for id: {}.".format(dataset_id)
        )

    first_sample = get_next_sample(dataset)
    if not first_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the first sample.",
        )
    first_sample.ensure_string_content()

    return first_sample
