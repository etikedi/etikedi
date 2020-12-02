from io import StringIO

import numpy as np
import pandas as pd
from pandas import DataFrame

from backend.models import Dataset
from ..config import app, db
from ..models import Association, Sample


def prepare_dataset_for_active_learning(dataset: Dataset) -> DataFrame:
    """
    Prepares the dataset for the active learning module

    The returned dataframe should have the following characteristics:
    - the index are integers equal to the database ids
    - a column label with the labels already assigned
    - remaining columns are labels
    """
    buffer = StringIO(dataset.features)
    sample_df = pd.read_csv(buffer).set_index("ID")

    # @todo: investigate what the following index shenanigans actually does
    all_sample_ids = db.query(Sample.id).filter(Sample.dataset_id == dataset.id).all()
    all_sample_ids = np.array(all_sample_ids)[:, 0]

    sample_df.index = pd.Int64Index(all_sample_ids)

    associated_labels = (
        db.query(Association.sample_id, Association.label_id)
            .join(Association.sample)
            .filter(Sample.dataset == dataset)
            .all()
    )

    label_df = pd.DataFrame(associated_labels, columns=["ID", "label"]).set_index("ID")
    df = pd.concat([sample_df, label_df], axis=1)

    return df
