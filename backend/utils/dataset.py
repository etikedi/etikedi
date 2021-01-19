from ..config import db
from ..models import Dataset, Association, Sample


def number_of_total_samples(dataset: Dataset) -> int:
    return db.query(Sample).filter(Sample.dataset == dataset).count()


def number_of_labelled_samples(dataset: Dataset) -> int:
    return db.query(Association).join(Association.sample) \
        .filter(Sample.dataset == dataset) \
        .count()


def number_of_features(dataset: Dataset) -> int:
    return len(dataset.feature_names.split(','))