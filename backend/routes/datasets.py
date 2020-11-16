from typing import List

from fastapi import Depends, UploadFile, File, Form, HTTPException, APIRouter
from sqlalchemy.orm import Session

from ..config import db
from ..importing import import_dataset
from ..models import Dataset, DatasetDTO, User, Table, Image, Text
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
        current_user: User = Depends(get_current_active_user)
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
        ensure_incomplete=True
    )

    return dataset
