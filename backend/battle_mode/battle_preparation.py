from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from ..config import db
from ..models import ALBattleConfig, Dataset
from ..utils import timeit


class BattlePreparation:

    @staticmethod
    def prepare_experiment(config: ALBattleConfig, dataset_id: int):
        labeled_samples_as_df = BattlePreparation._transform_dataset(dataset_id)
        cb_sample = BattlePreparation._classification_boundaries_raster(
            dataset_id,
            config.PLOT_CONFIG.CLASSIFICATION_BOUNDARIES.NBR_OF_RANDOM_SAMPLE)
        return labeled_samples_as_df, cb_sample

    @staticmethod
    @timeit
    def _classification_boundaries_raster(dataset_id, size: int):
        labelled = list(filter(lambda smpl: smpl.labels != [], db.get(Dataset, dataset_id).samples))
        feature_df = pd.DataFrame([
            sample.feature_dict() for sample in labelled
        ])
        feature_domains = {}
        for feature in feature_df.columns:
            dtype = feature_df.dtypes[feature]
            if dtype == int or dtype == float:
                feature_domains[feature] = np.array([feature_df[feature].min(), feature_df[feature].max()],
                                                    dtype)
            else:
                feature_domains[feature] = feature_df[feature].unique()
        random_sample_tmp = []
        for i in range(size):
            new_sample = {}
            for feature in feature_df.columns:
                domain = feature_domains[feature]
                if domain.dtype == int:
                    new_sample[feature] = np.random.randint(low=domain[0], high=domain[1] + 1)
                elif domain.dtype == float:
                    new_sample[feature] = np.random.uniform(low=domain[0], high=domain[1])
                else:
                    new_sample[feature] = np.random.choice(domain)
            random_sample_tmp.append(new_sample)

        return pd.DataFrame(columns=feature_df.columns, data=random_sample_tmp)

    @staticmethod
    @timeit
    def _transform_dataset(dataset_id: int):
        dataset: Dataset = db.get(Dataset, dataset_id)
        feature_names: List[str] = dataset.feature_names.split(",")
        frame = pd.DataFrame(data=
                             [{f_name: f for (f_name, f) in
                               zip(feature_names + ['LABEL', "DB_ID"],
                                   sample.extract_feature_list() + [sample.labels[0].name, sample.id])}
                              for sample in dataset.samples if sample.labels != []])
        # TODO some models / query_strategies need number based label
        # labels = frame['LABEL'].unique()
        # label2Int = {label: i for i, label in enumerate(labels)}
        # frame['Label'] = frame['LABEL'].map(label2Int)
        # int2Label: dict[int, str] = {i: label for label, i in label2Int.items()}
        return frame
