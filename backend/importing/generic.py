import csv
from zipfile import ZipFile
from typing import Type
from pathlib import Path

from ..config import db
from ..models import Dataset, Sample


def import_dataset(dataset: Dataset, sample_class: Type[Sample], feature_path: Path, content_path: Path):
    """
    Creates samples from the given json list of objects.

    If no `feature_attributes` are specified, all attributes besides the one specified by `content_attribute`
    are taken into account.

    :param dataset:
    :param sample_class:
    :return:
    """
    with feature_path.open('r') as feature_file, content_path.open('rb') as content_file:
        lines = list(csv.reader(feature_file))
        zip_file = ZipFile(content_file, 'r')

        feature_names = lines[0]
        total = len(lines)
        samples = []
        labels = set()

        for index, line in enumerate(lines[1:], 1):
            identifier, *feature_set, label = line
            content = zip_file.read(f'{int(identifier)}.raw')
            labels.add(label)

            sample = sample_class()
            sample.dataset = dataset
            sample.features = feature_set
            sample.content = content
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
