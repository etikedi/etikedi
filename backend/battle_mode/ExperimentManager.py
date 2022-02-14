from __future__ import annotations  # necessary in order to use ExperimentManager as type hint

from multiprocessing import Queue
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd

from ..utils import ValidationError
from .additional_experiment_validation import validate_config
from .experiment import ALExperimentProcess, MetricsDFKeys, EventType, ResultType
from ..config import logger
from ..models import AlExperimentConfig, Metric, Status


class ExperimentManager:
    """Manages (asynchronous) execution of two AL-strategies"""

    _manager: Dict[int, ExperimentManager] = {}

    @staticmethod
    def has_manager(dataset_id: int):
        return dataset_id in ExperimentManager._manager

    @staticmethod
    def get_manager(dataset_id):
        return ExperimentManager._manager[dataset_id]

    def __init__(self, dataset_id: int, config_one: AlExperimentConfig, config_two: AlExperimentConfig):
        self.dataset_id: int = dataset_id
        validate_config(dataset_id, config_one)
        validate_config(dataset_id, config_two)
        self.configs = (config_one, config_two)
        self.started_flags: List[bool, bool] = [False, False]
        self.setup_completed_flags: List[bool, bool] = [False, False]
        self.finished_flags: List[bool, bool] = [False, False]
        self.results: List[Optional[ResultType], Optional[ResultType]] = [None, None]
        self.last_reported_time: Optional[Tuple[float, bool]] = None  # reported time, true if experiment one
        self.metric: Optional[Metric] = None
        self.queues = [Queue(), Queue()]
        self.experiments: List[ALExperimentProcess] = [
            ALExperimentProcess(i, dataset_id, self.configs[i], self.queues[i]) for i in [0, 1]]
        if dataset_id in ExperimentManager._manager:
            logger.warn(f"Replacing existent manager for id {dataset_id}")
            ExperimentManager._manager[dataset_id].terminate()
        ExperimentManager._manager[dataset_id] = self

    def start(self):
        for exp in self.experiments:
            exp.start()
        self.started_flags = [True for _ in self.started_flags]

    def get_metrics(self) -> Metric:
        if self.metric is not None:
            return self.metric
        self.assert_finished()
        self._poll_results_if_not_present()
        combined: List = []
        m0 = self.results[0].metric_data
        m1 = self.results[1].metric_data
        for idx in range(max(len(m0), len(m1))):
            combined.append((m0[idx] if idx < len(m0) else None, m1[idx] if idx < len(m1) else None))
        self.metric = Metric(iterations=combined)
        return self.metric

    def get_learning_curve_data(self) -> pd.DataFrame:
        # convert to long form for altair
        self.assert_finished()
        self._poll_results_if_not_present()

        def gen(idx, key):
            return [(it, key, item[MetricsDFKeys.ACC]) for it, item in self.results[idx].df.iterrows()]

        rows = gen(0, "First")
        rows += gen(1, "Second")
        return pd.DataFrame(data=rows, columns=["Iteration", "Experiment", "Value"])

    def get_confidence_his_data(self) -> Tuple[List[List[float]], List[List[float]]]:
        # return
        self.assert_finished()
        self._poll_results_if_not_present()

        def gen(experiment_idx: int):
            data_over_iterations = []
            for _, row in self.results[experiment_idx].raw_predictions.iterrows():
                data_over_iterations.append(list(np.max(row)))
            return data_over_iterations

        return gen(0), gen(1)

    def get_data_map_data(self):
        self.assert_finished()
        self._poll_results_if_not_present()

        def gen(exp_idx: int):
            r = self.results[exp_idx]
            raw_predicts = r.raw_predictions
            data = []
            for smpl in raw_predicts.columns:
                confidence = raw_predicts[smpl].map(lambda x: max(x)).mean()
                variance = raw_predicts[smpl].map(lambda x: x.index(max(x))).var()
                correctness = raw_predicts[smpl].map(lambda x: x.index(max(x)) == r.correct_labelAsIdx[smpl]).mean()
                data.append({'Confidence': confidence,
                             'Variability': variance,
                             'Correctness': correctness,
                             'SampleID': smpl})
            return pd.DataFrame(data)

        return gen(0), gen(1)

    def get_status(self) -> Status:
        """ @return
                -1 if both are finished
                -2 if no (new) data is available
                time in seconds if at least one has finished one iteration
                """
        self.assert_started()
        times = [self.poll_process(i) for i in [0, 1]]
        if not all(self.setup_completed_flags):
            return Status(code=Status.Code.IN_SETUP)
        if all(self.finished_flags):
            return Status(code=Status.Code.COMPLETED)  # experiments are finished: both results are reported
        if all(t is None for t in times):
            return Status(code=Status.Code.TRAINING)  # experiments not finished and no new time
        if self.last_reported_time is None:
            times = list(filter(lambda t: t is not None, times))
            t = max(times)
            self.last_reported_time = t, times.index(t)
            return Status(code=Status.Code.TRAINING, time=max(times))
        for i, t in enumerate(times):
            if t is not None and (t > self.last_reported_time[0] or i == self.last_reported_time[1]):
                self.last_reported_time = t, i
        return Status(code=Status.Code.TRAINING, time=self.last_reported_time[0])

    def assert_started(self):
        if not all(self.started_flags):
            raise ValidationError(
                f"At least one experiment was not started ({[e for e in [0, 1] if not self.started_flags[e]]})")

    def assert_finished(self):
        self.assert_started()
        if not all(self.finished_flags):  # TODO
            for exp_idx in [0, 1]:
                if self.results[exp_idx] is None:
                    self.poll_process(exp_idx)
            if not all(self.finished_flags):
                raise ValidationError(
                    f"At least one experiment is not finished ({[e for e in [0, 1] if not self.finished_flags[e]]})")

    def _poll_results_if_not_present(self):
        self.assert_finished()
        if all(r is not None for r in self.results):
            return
        for exp_idx in [0, 1]:
            if self.results[exp_idx] is None:
                self.poll_process(exp_idx)

    def poll_process(self, exp_idx: int) -> Optional[float]:
        """
        @param exp_idx the queue of experiment one or two
        @return If the result was not send -> return the last send time
                If no new time was reported or is finished return None
        """
        if exp_idx not in [0, 1]:
            raise ValidationError(f"index of experiment was neither 0 nor 1: {exp_idx}")
        if self.finished_flags[exp_idx]:
            return None
        last_time = None
        queue = self.queues[exp_idx]
        while not queue.empty():
            event = queue.get_nowait()
            if event['Type'] == EventType.INFO:
                last_time = event['Value']
            elif event['Type'] == EventType.SETUP_COMPLETED:
                self.setup_completed_flags[exp_idx] = True
            elif event['Type'] == EventType.RESULT:
                self.results[exp_idx] = event['Value']
                self.experiments[exp_idx].join()
                self.finished_flags[exp_idx] = True
                return None

        return last_time

    def terminate(self):
        logger.info(f"Terminating experiment with ID: {getattr(self,'dataset_id', 'Unknown')}")
        if not hasattr(self, 'finished_flags') or hasattr(self, 'experiments'):
            return
        for exp_ind, finished in enumerate(self.finished_flags):
            if not finished:
                self.experiments[exp_ind].kill()
        if not hasattr(self, 'queues'):
            return
        for q in self.queues:
            q.close()

    def __del__(self):
        self.terminate()
