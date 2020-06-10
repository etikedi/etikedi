import json
from typing import List, Type, Union

from ..config import db
from ..models import Dataset, Sample


def import_dataset(dataset: Dataset, data: Union[List[dict], str], sample_class: Type[Sample], content_attribute: str, feature_attributes: List[str] = None):
    """
    Creates samples from the given json list of objects.

    If no `feature_attributes` are specified, all attributes besides the one specified by `content_attribute`
    are taken into account.

    :param dataset:
    :param data:
    :param sample_class:
    :param content_attribute:
    :param feature_attributes:
    :return:
    """
    if isinstance(data, str):
        data = json.loads(data)

    if isinstance(data, list) and all(isinstance(entry, dict) for entry in data):
        samples = []
        total = len(data)

        for index, raw_sample in enumerate(data, 1):
            sample = sample_class()
            sample.dataset = dataset

            try:
                sample.content = json.dumps(raw_sample[content_attribute])
            except KeyError:
                raise ValueError('Sample {} has no content attribute {}: {}'.format(index, content_attribute, raw_sample))

            if feature_attributes is None:
                feature_attributes = set(raw_sample.keys()) - { content_attribute }

            try:
                sample.features = json.dumps({
                    key: raw_sample[key]
                    for key in feature_attributes
                })
            except KeyError:
                raise ValueError('Sample {} has a missing feature attribute'.format(raw_sample))

            samples.append(sample)

            if index == total:
                print('Done importing dataset {}'.format(dataset))
                db.session.add_all(samples)
                db.session.commit()
            elif index % 1000 == 0:
                print('{:.2f}% imported ({}/{})'.format((index / total) * 100, index, total))
                db.session.add_all(samples)
                db.session.commit()
                samples = []
