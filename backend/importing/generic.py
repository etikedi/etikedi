import pandas as pd
from zipfile import ZipFile
from typing import Type
from pathlib import Path

from sqlalchemy.orm.exc import NoResultFound

from ..config import db
from ..models import Dataset, Sample, Label, User, Association


def import_dataset(dataset: Dataset, sample_class: Type[Sample], feature_path: Path, content_path: Path, user: User = None):
    if not user:
        try:
            user = User.query.first()
        except NoResultFound:
            raise ValueError('To import a dataset, there must be at least one user in the system (for creating the association between samples and lables)')

    with feature_path.open('r') as feature_file, content_path.open('rb') as content_file:
        df = pd.read_csv(feature_file).set_index('ID')
        feature_df = df.drop(['LABEL'], axis=1)

        dataset.features = feature_df.to_csv()
        dataset.feature_names = ','.join(feature_df.columns)

        all_labels = {
            label_name: Label(name=label_name, dataset=dataset)
            for label_name in df['LABEL'].unique()
        }
        db.session.add_all(all_labels.values())
        db.session.commit()

        zip_file = ZipFile(content_file, 'r')

        total, samples, associations = len(df.index), [], []
        for index, (identifier, label_name) in enumerate(df['LABEL'].iteritems()):
            content = zip_file.read(f'{int(identifier)}.raw')

            sample = sample_class()
            sample.dataset = dataset
            sample.content = content
            samples.append(sample)

            if label_name and label_name in all_labels:
                associations.append(Association(
                    sample=sample,
                    label=all_labels[label_name],
                    user=user
                ))

            if index % 1000 == 0:
                print('{:.2f}% imported ({}/{})'.format((index / total) * 100, index, total))
                db.session.add_all(samples)
                db.session.commit()
                db.session.add_all(associations)
                db.session.commit()
                samples = []
                associations = []

        print('Done importing dataset {}'.format(dataset))
        db.session.add_all(samples)
        db.session.commit()
        db.session.add_all(associations)
        db.session.commit()
