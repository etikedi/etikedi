from typing import List, Dict

from ..config import db
from ..models import Sample, Label, Dataset, Association
from ..models.iris_model import Flower


def samples_of_dataset(name: str) -> List[Sample]:
    """
    Returns all samples of the dataset with the given name.

    Exception:
        ValueError: There is no dataset with the given name.
    """
    dataset: Dataset = db.session.query(Dataset).filter(
        Dataset.name == name
    ).first()

    if not dataset:
        raise ValueError('There is no dataset with id "{}"'.format(name))

    return dataset.items


def labels_of_dataset(name: str) -> List[Label]:
    """
    Returns all labels of the dataset with the given name.

    Exception:
        ValueError: There is no dataset with the given name.
    """
    dataset: Dataset = db.session.query(Dataset).filter(
        Dataset.name == name
    ).first()

    if not dataset:
        raise ValueError('There is no dataset with name "{}"'.format(name))

    return dataset.labels


def samples_to_feature_dict(samples: List[Sample]) -> Dict[int, dict]:
    """
    Converts a list of samples to a dict.

    The returned dict has the ids of the sample as key and dictionaries containing the features
    loaded from the stored json as values.
    """
    return {
        sample.id: sample.features
        for sample in samples
    }

def check_for_label(sample_id):
    label = db.session.query(Association).filter(Association.sample_id == sample_id).first()
    return label


def query_flowers():
    flowers = db.session.query(Flower).all()
    db.session.commit()
    return flowers


def dataset_name_by_dataset_id(dataset_id):
    dataset = db.session.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        return ""
    return dataset.name

if __name__ == "__main__":
    all_labels = labels_of_dataset('Lorem')
    print(all_labels)

    all_samples = samples_of_dataset('Lorem')
    print(all_samples)

    feature_dict = samples_to_feature_dict(all_samples)
    print(feature_dict)
