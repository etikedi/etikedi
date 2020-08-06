import numpy as np
import pandas as pd
from zipfile import ZipFile
from typing import Type, Union
from pathlib import Path

from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from ..config import db, app
from ..models import Dataset, Sample, Label, User, Association


def import_dataset(
    dataset: Dataset,
    sample_class: Type[Sample],
    features: Union[Path, FileStorage],
    content: Union[Path, FileStorage],
    user: User = None,
    ensure_incomplete=True,
):
    if not user:
        try:
            user = User.query.first()
        except NoResultFound:
            raise ValueError(
                "To import a dataset, there must be at least one user in the system (for creating the association between samples and lables)"
            )

    if isinstance(features, Path):
        feature_file = features.open("r")
        df = pd.read_csv(feature_file).set_index("ID")
        feature_file.close()
    elif isinstance(features, FileStorage):
        df = pd.read_csv(features).set_index("ID")
    else:
        raise ValueError("The features argument must be either a Path or FileStorage")

    try:
        zip_file = ZipFile(content, "r")
    except AttributeError:
        raise ValueError("The content argument must be either a Path or FileStorage")

    feature_df = df.drop(["LABEL"], axis=1)

    dataset.features = feature_df.to_csv()
    dataset.feature_names = ",".join(feature_df.columns)

    all_labels = {
        label_name: Label(name=label_name, dataset=dataset)
        for label_name in df["LABEL"].unique()
    }
    db.session.add_all(all_labels.values())
    db.session.commit()

    total, samples, associations = len(df.index), [], []
    for index, (identifier, label_name) in enumerate(df["LABEL"].iteritems()):
        content = zip_file.read(f"{int(identifier)}.raw")

        sample = sample_class()
        sample.dataset = dataset
        sample.content = content
        samples.append(sample)

        if label_name and label_name in all_labels:
            associations.append(
                Association(sample=sample, label=all_labels[label_name], user=user)
            )

        if index % 1000 == 0:
            print(
                "{:.2f}% imported ({}/{})".format((index / total) * 100, index, total)
            )
            db.session.add_all(samples)
            db.session.commit()
            db.session.add_all(associations)
            db.session.commit()
            samples = []
            associations = []

    print("Done importing dataset {}".format(dataset))
    db.session.add_all(samples)
    db.session.commit()
    db.session.add_all(associations)
    db.session.commit()

    if ensure_incomplete:
        number_of_samples = Sample.query.filter(Sample.dataset == dataset).count()
        number_of_associations = (
            db.session.query(Association.sample_id)
            .join(Association.sample)
            .filter(Sample.dataset == dataset)
            .count()
        )

        if number_of_samples == number_of_associations:
            app.logger.info(f"{dataset} is already complete. Thinning it out!")
            sample_ids = (
                db.session.query(Association.sample_id)
                .join(Association.sample)
                .filter(Sample.dataset == dataset)
                .all()
            )
            flat_sample_ids = list(map(int, np.array(sample_ids)[:, 0]))
            to_delete = flat_sample_ids[::3]

            # Dirty; Use a raw query because otherwise SQLAlchemy unsuccessfully tries to synchronise the
            # current session
            db.session.execute(
                f'DELETE FROM association WHERE sample_id IN ({",".join(map(str, to_delete))})'
            )
            db.session.commit()
