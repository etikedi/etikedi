from fastapi import Depends
from sqlalchemy.orm import Session

from ..config import db
from ..models import Dataset, Label, Sample


def can_assign(sample_id: int, label_id: int):
    """ Checks if the sample can be assigned to the given label. """
    return bool(
        db.query(Dataset, Sample, Label)
        .filter(Dataset.id == Sample.dataset_id)
        .filter(Dataset.id == Label.dataset_id)
        .filter(Sample.id == sample_id)
        .filter(Label.id == label_id)
        .count()
    )
