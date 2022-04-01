import base64
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import IO, Type, Tuple
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sqlalchemy import Text
from sqlalchemy.orm.exc import NoResultFound

from ..config import logger, db
from ..models import Dataset, Sample, Label, Association, User


def import_dataset(
    name: str,
    sample_class: Type[Sample],
    features: IO,
    content: IO,
    user: User = None,
    ensure_incomplete=True,
) -> Tuple[Dataset, int]:
    if not user:
        try:
            user = db.query(User).first()
        except NoResultFound:
            raise ValueError(
                "To import a dataset, there must be at least one user in the system "
                "(for creating the association between samples and labels)"
            )

    if isinstance(features, Path):
        feature_file = features.open("r")
        df = pd.read_csv(feature_file).set_index("ID")
        feature_file.close()
    elif isinstance(features, SpooledTemporaryFile):
        features.rollover()
        df = pd.read_csv(features._file).set_index("ID")
    else:
        raise ValueError("The features argument must be either a Path or FileStorage")

    try:
        if isinstance(content, SpooledTemporaryFile):
            content.rollover()
            zip_file = ZipFile(content._file, "r")
        else:
            zip_file = ZipFile(content, "r")
    except AttributeError:
        raise ValueError("The content argument must be either a Path or FileStorage")

    feature_df = df.drop(["LABEL"], axis=1)

    dataset = Dataset(
        name=name,
        features=feature_df.to_csv(),
        feature_names=",".join(feature_df.columns),
    )

    all_labels = {
        label_name: Label(name=str(label_name), dataset=dataset)
        for label_name in df["LABEL"].unique()
    }
    db.add_all(all_labels.values())
    db.commit()

    total, samples, associations = len(df.index), [], []
    # iterate over rows in dataframe (identifier = ID Column = index of row
    for identifier, row in df.iterrows():
        label_name = row["LABEL"]
        content = zip_file.read(f"{int(identifier)}.raw")
        sample = sample_class()
        sample.dataset = dataset

        # get features from dataframe (all columns expect ID and LABEL
        sample_features = row.drop("LABEL")
        # test if features exist for sample
        if sample_features.empty:
            logger.error(
                f"Missing sample id in feature set: {identifier}, skipping sample"
            )
        else:
            # save as json
            sample.features = sample_features.to_json()
            # get type of content and convert to text if needed
            content_type = sample_class.content.property.columns[0].type
            if isinstance(content_type, Text):
                content = content.decode("utf-8")

            sample.content = content
            samples.append(sample)

            if label_name and label_name in all_labels:
                associations.append(
                    Association(sample=sample, label=all_labels[label_name], user=user)
                )

        # save intermediate state
        if identifier % 1000 == 0:
            logger.info(
                "{:.2f}% imported ({}/{})".format(
                    (identifier / total) * 100, identifier, total
                )
            )
            db.add_all(samples)
            db.commit()
            db.add_all(associations)
            db.commit()
            samples = []
            associations = []

    logger.info("Done importing dataset {}".format(dataset))
    db.add_all(samples)
    db.commit()
    db.add_all(associations)
    db.commit()

    number_of_samples = db.query(Sample).filter(Sample.dataset == dataset).count()
    if ensure_incomplete:
        number_of_associations = (
            db.query(Association.sample_id)
            .join(Association.sample)
            .filter(Sample.dataset == dataset)
            .count()
        )

        if number_of_samples == number_of_associations:
            logger.info(f"{dataset} is already complete. Thinning it out!")
            sample_ids = (
                db.query(Association.sample_id)
                .join(Association.sample)
                .filter(Sample.dataset == dataset)
                .all()
            )
            flat_sample_ids = list(map(int, np.array(sample_ids)[:, 0]))
            to_delete = flat_sample_ids[::3]

            # Dirty; Use a raw query because otherwise SQLAlchemy unsuccessfully tries to synchronise the
            # current session
            db.execute(
                f'DELETE FROM association WHERE sample_id IN ({",".join(map(str, to_delete))})'
            )
            db.commit()

    return dataset, number_of_samples
