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
        self.pipe_one, process_endpoint_one = Pipe(duplex=False)  # only process has to use pipe
        self.pipe_two, process_endpoint_two = Pipe(duplex=False)
        self.experiment_one: ALExperimentProcess = ALExperimentProcess(
            self._transform_dataset(), self.config_one, process_endpoint_one)
        self.experiment_two: ALExperimentProcess = ALExperimentProcess(
            self._transform_dataset(), self.config_two, process_endpoint_two)
        if dataset_id in ExperimentManager._manager:
            logger.warn(f"Replacing existent manager for id {dataset_id}")
        ExperimentManager._manager[dataset_id] = self

    def start(self):
        self.experiment_one.start()
        self.experiment_two.start()

    def get_metrics(self):
        if self.experiment_one.is_alive() or self.experiment_two.is_alive():
            raise ValueError("Experiment has to be run first")
        return self.experiment_one.calculate_metrics(), self.experiment_two.calculate_metrics()

    def get_status(self) -> int:
        """ @return
                -1 if both are finished
                -2 if no data is available
                time in seconds if at least one is finished
                """
        # TODO estimate remaining time
        if not (self.experiment_one.is_alive() and self.experiment_two.is_alive()):
            return -1

        time_one = self.pipe_one.recv() if self.pipe_one.poll() else None
        time_two = self.pipe_two.recv() if self.pipe_two.poll() else None
        self._clear_pipes()
        if time_one is None and time_two is None:
            return -2  # no estimation can be made -> not necessarily a failure state
        if time_one is None:
            return time_two
        if time_two is None:
            return time_one
        return max(time_one, time_two)

    def _transform_dataset(self) -> pd.DataFrame:
        dataset: Dataset = db.get(Dataset, self.dataset_id)
        feature_names: List[str] = dataset.feature_names.split(",")
        frame = pd.DataFrame(data=
                             [sample.extract_feature_list() + [sample.labels[0].name]
                              for sample in dataset.samples if sample.labels != []],
                             columns=feature_names + ["LABEL"])
        print(f"There are {len(frame)} labeled samples ({round(len(frame) / len(dataset.samples) * 100, 2)})%")
        return frame

    def _clear_pipes(self):
        """Discard all further messages"""
        while self.pipe_one.poll():
            self.pipe_one.recv()
        while self.pipe_two.poll():
            self.pipe_two.recv()
