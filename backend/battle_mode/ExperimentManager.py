from typing import List

from ..models import Dataset
from ..config import db
from .experiment import AL_Experiment
import pandas as pd


class ExperimentManager:
    """Manages (asynchronous) execution of to AL-strategies"""

    def __init__(self, dataset_id: int, config_one, config_two):
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

        self.experiment_one.run_experiment(verbose=1)
        self.experiment_one.calculate_metrics()
        self.experiment_one.plot_metrics()
        return self

    def get_metrics(self):
        if not self.was_executed:
            raise Exception("Experiment has to be run first")
        return self.experiment_one.metrics, self.experiment_two.metrics

    def _from_dataset(self, config) -> AL_Experiment:
        dataset: Dataset = db.get(Dataset, self.dataset_id)
        feature_names: List[str] = dataset.feature_names.split(",")
        frame = pd.DataFrame(data=
                             [sample.extract_feature_list() + [sample.labels[0].name]
                              for sample in dataset.samples if sample.labels != []],
                             columns=feature_names + ["LABEL"])
        print(f"There are {len(frame)} labeled samples ({round(len(frame) / len(dataset.samples) * 100, 2)})%")
        return AL_Experiment(frame)
