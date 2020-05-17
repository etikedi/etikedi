from typing import List, Dict

from config import db
from models import Sample, Label, Dataset, Association
from models.label_queue import LabelQueue, Flower


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
        raise ValueError('There is no dataset with name "{}"'.format(name))

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


def add_to_label_queue(sample_ids):
    for sample_id in sample_ids:
        db.session.add(LabelQueue(id=sample_id))
    db.session.commit()
    db.session.close()


def delete_from_label_queue(query_sample_ids):
    for sample_id in query_sample_ids:
        LabelQueue.query.filter_by(id=sample_id).delete()
    db.session.commit()
    db.session.close()


def query_new_labels(sample_id):
    association = db.session.query(Association).filter_by(sample_id=sample_id).first()
    db.session.commit()
    return association


def to_be_labeled():
    sample_ids = db.session.query(LabelQueue).all()
    db.session.commit()
    return sample_ids


def query_flowers():
    flowers = db.session.query(Flower).all()
    db.session.commit()
    return flowers

# all_labels = labels_of_dataset('Lorem')
# print(all_labels)
#
# all_samples = samples_of_dataset('Lorem')
# print(all_samples)
#
# feature_dict = samples_to_feature_dict(all_samples)
# print(feature_dict)
