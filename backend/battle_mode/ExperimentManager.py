from __future__ import annotations  # necessary in order to use ExperimentManager as type hint

from multiprocessing.connection import Pipe
from typing import List, Dict

import pandas as pd

from .experiment import ALExperimentProcess
from ..config import db, logger
from ..models import Dataset, AlExperimentConfig


class ExperimentManager:
    """Manages (asynchronous) execution of to AL-strategies"""

    _manager: Dict[int, ExperimentManager] = {}

    @classmethod
    def has_manager(cls, dataset_id: int):
        return dataset_id in ExperimentManager._manager

    @classmethod
    def get_manager(cls, dataset_id):
        return ExperimentManager._manager[dataset_id]

    def __init__(self, dataset_id: int, config_one: AlExperimentConfig, config_two: AlExperimentConfig):
        self.was_executed = False
        self.dataset_id: int = dataset_id
        self.config_one = config_one
        self.config_two = config_two
        self.experiment_one: AL_Experiment = self._from_dataset(self.config_one)
        self.experiment_two: AL_Experiment = self._from_dataset(self.config_two)

    def run(self):
        self.experiment_one.run_experiment(verbose=1)
        self.experiment_one.calculate_metrics()
        self.experiment_one.plot_metrics()

        self.experiment_two.run_experiment(verbose=1)
        self.experiment_two.calculate_metrics()
        self.experiment_two.plot_metrics()
        self.was_executed = True
        return self

    def get_metrics(self):
        if not self.was_executed:
            raise Exception("Experiment has to be run first")
        return self.experiment_one.metrics, self.experiment_two.metrics

    def _from_dataset(self, config: AlExperimentConfig) -> AL_Experiment:
        dataset: Dataset = db.get(Dataset, self.dataset_id)
        feature_names: List[str] = dataset.feature_names.split(",")
        frame = pd.DataFrame(data=
                             [sample.extract_feature_list() + [sample.labels[0].name]
                              for sample in dataset.samples if sample.labels != []],
                             columns=feature_names + ["LABEL"])
        print(f"There are {len(frame)} labeled samples ({round(len(frame) / len(dataset.samples) * 100, 2)})%")
        return AL_Experiment(frame, config)
