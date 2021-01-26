from io import StringIO
from typing import Tuple, Dict

import numpy as np
import pandas as pd
from pandas import DataFrame

from backend.models import Dataset
from ..config import app, db
from ..models import Association, Sample
from .types import *


def prepare_dataset_for_active_learning(dataset: Dataset) -> Tuple[DataFrame, Dict[SampleID, InternalSampleID], Dict[InternalSampleID, SampleID]]:
    """
    Prepares the dataset for the active learning module

    The returned dataframe should have the following characteristics:
    - the index are integers starting from 0
    - a column label with the labels already assigned
    - remaining columns are features
    """
    buffer = StringIO(dataset.features)
    sample_df = pd.read_csv(buffer).drop("ID", "columns")  # We could use "ID" as an index but it is not guaranteed to be 0-based

    all_sample_ids = db.query(Sample.id).filter(Sample.dataset_id == dataset.id).all()
    all_sample_ids = np.array(all_sample_ids)[:, 0]

    sample_id_mapping: Dict[SampleID, InternalSampleID] = dict(zip(all_sample_ids, sample_df.index))
    reverse_sample_id_mapping: Dict[InternalSampleID, SampleID] = dict(zip(sample_df.index, all_sample_ids))

    associated_labels = (
        db.query(Association.sample_id, Association.label_id)
            .join(Association.sample)
            .filter(Sample.dataset == dataset)
            .all()
    )

    label_df = pd.DataFrame(associated_labels, columns=["ID", "label"]).set_index("ID")
    label_df.index = pd.Int64Index([sample_id_mapping[db_id] for db_id in label_df.index])

    df = pd.concat([sample_df, label_df], axis=1)

    return df, sample_id_mapping, reverse_sample_id_mapping


def reverse_dict(d: Dict[int, int]) -> Dict[int, int]:
    return dict(zip(d.values(), d.keys()))
