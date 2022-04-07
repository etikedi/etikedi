from __future__ import annotations  # necessary in order to use ExperimentManager as type hint

import asyncio
import functools
from asyncio import Future
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue
from typing import List, Dict, Tuple, Optional

import pandas as pd

from .additional_experiment_validation import validate_else_throw
from .battle_preparation import BattlePreparation
from .experiment import ALExperimentProcess
from .battle_analyzer import BattleAnalyzer
from ..config import logger
from ..models import (
    ALBattleConfig,
    Metric,
    Status,
    ExperimentResults,
    ExperimentQueueEventType)
from ..utils import ValidationError


class BattleManager:
    """Manages (asynchronous) execution of two AL-strategies"""

    # experiment_id -> Experiment
    _manager: Dict[int, ActiveBattleHolder] = {}
    _finished_manager: Dict[int, BattleAnalyzer] = {}
    _experiment_id_counter = 0

    @staticmethod
    def _next_id():
        next_id = BattleManager._experiment_id_counter
        BattleManager._experiment_id_counter = next_id + 1
        return next_id

    @staticmethod
    def has_active_manager(experiment_id: int):
        return experiment_id in BattleManager._manager

    @staticmethod
    def has_finished_manager(experiment_id: int):
        return experiment_id in BattleManager._finished_manager

    @staticmethod
    def get_active_manager(experiment_id: int):
        return BattleManager._manager[experiment_id]

    @staticmethod
    def set_finished_manager(manager: BattleAnalyzer):
        if manager.experiment_id in BattleManager._finished_manager:
            logger.warn("Replacing finished existing manager for id: " + str(manager.experiment_id))
        BattleManager._finished_manager[manager.experiment_id] = manager

    @staticmethod
    def get_or_create_finished_manager(experiment_id: int) -> BattleAnalyzer:
        if experiment_id not in BattleManager._finished_manager:
            manager: BattleAnalyzer = BattleManager._manager[experiment_id].create_battle_analyzer()
            BattleManager._finished_manager[experiment_id] = manager
        return BattleManager._finished_manager[experiment_id]

    @staticmethod
    def get_experiment_id_counter():
        return BattleManager._experiment_id_counter

    @staticmethod
    def create_and_start(dataset_id, battle_config):
        validate_else_throw(dataset_id, battle_config)
        experiment_id = BattleManager._next_id()
        holder = ActiveBattleHolder(experiment_id, dataset_id, battle_config)
        BattleManager._manager[experiment_id] = holder
        return experiment_id

    @staticmethod
    def remove_or_terminate(experiment_id):
        if BattleManager.has_active_manager(experiment_id):
            BattleManager._manager[experiment_id].terminate()
            del BattleManager._manager[experiment_id]
        elif experiment_id in BattleManager._finished_manager:
            del BattleManager._finished_manager[experiment_id]
        else:
            raise ValueError("No manager for ID: " + str(experiment_id))


class ActiveBattleHolder:
    def __init__(self, experiment_id: int, dataset_id: int, battle_config: ALBattleConfig):
        logger.info("Creating experiment for ID:" + str(experiment_id))
        self.dataset_id: int = dataset_id
        self.experiment_id = experiment_id
        self.config: ALBattleConfig = battle_config
        self.setup_completed_flags: List[bool, bool] = [False, False]
        self.finished_flags: List[bool, bool] = [False, False]
        self.results: List[Optional[ExperimentResults], Optional[ExperimentResults]] = [None, None]
        self.last_reported_time: Optional[Tuple[float, bool]] = None  # reported time, true if experiment one
        self.metric: Optional[Metric] = None
        self.queues = [Queue(), Queue()]
        # initialized in callback
        self.cb_sample: Optional[pd.DataFrame] = None  # generated samples for classification boundaries
        self.experiments: Tuple[ALExperimentProcess] = tuple()  # both processes running the experiments
        self.preparation_future: Optional[Future] = None  # waiting for async preparation
        self.prepare()

    def prepare(self):
        """
        Dataset preparation can be quite CPU intensive and should not block the networking request.
        Therefore, the preparation is moved to another process and the result is awaited via future + callback.
        """
        logger.info("Execution async preparation for ID: " + str(self.experiment_id))
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=1)  # execute in different process
        # noinspection PyTypeChecker
        self.preparation_future: Future = loop.run_in_executor(
            executor, functools.partial(BattlePreparation.prepare_experiment, self.config, self.dataset_id))
        self.preparation_future.add_done_callback(self._start_battle)

    def _start_battle(self, future: Future):
        """
        Collect the results of the preparation phase and start both experiment-processes.
        @param future: results of [ExperimentPreparation.prepare_experiment]
        """
        sample_df, cb_sample = future.result()
        self.cb_sample = cb_sample
        self.experiments = tuple([
            ALExperimentProcess(i, self.dataset_id, sample_df, self.config, self.queues[i],
                                cb_sample) for i in [0, 1]])
        for exp in self.experiments:
            exp.start()
        logger.info("Started experiments for ID: " + str(self.experiment_id))

    def get_status(self) -> Status:
        """ @return a [Status] object reflecting the current battle-status.
                0 if still in setup-phase (dataset-preparation or process in setup)
                1 if experiment-processes are running
                2 if finished with time in seconds if at least one has reported something
                """
        if not self.preparation_future.done():  # preparation callback not finished
            return Status(code=Status.Code.IN_SETUP)

        times = [self._poll_process(i) for i in [0, 1]]
        if not all(self.setup_completed_flags):
            return Status(code=Status.Code.IN_SETUP)
        if all(self.finished_flags):
            self.create_battle_analyzer()
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

    def create_battle_analyzer(self) -> BattleAnalyzer:
        self.assert_finished()
        self._poll_results_if_not_present()
        manager = BattleAnalyzer(
            experiment_id=self.experiment_id,
            dataset_id=self.dataset_id,
            config=self.config,
            cb_sample=self.cb_sample,
            result_one=self.results[0],
            result_two=self.results[1]
        )
        return manager

        # assertions

    def assert_finished(self):
        if not self.preparation_future.done():
            raise ValidationError('Preparation unfinished.')
        if not all(self.finished_flags):  # TODO
            for exp_idx in [0, 1]:
                if self.results[exp_idx] is None:
                    self._poll_process(exp_idx)
            if not all(self.finished_flags):
                raise ValidationError(
                    f"At least one experiment is not finished ({[e for e in [0, 1] if not self.finished_flags[e]]})")

    def _poll_results_if_not_present(self):
        self.assert_finished()
        if all(r is not None for r in self.results):
            return
        for exp_idx in [0, 1]:
            if self.results[exp_idx] is None:
                self._poll_process(exp_idx)

    def _poll_process(self, exp_idx: int) -> Optional[float]:
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
            if event['Type'] == ExperimentQueueEventType.INFO:
                last_time = event['Value']
            elif event['Type'] == ExperimentQueueEventType.SETUP_COMPLETED:
                self.setup_completed_flags[exp_idx] = True
            elif event['Type'] == ExperimentQueueEventType.RESULT:
                self.results[exp_idx] = event['Value']
                self.experiments[exp_idx].join()
                self.finished_flags[exp_idx] = True
                return None

        return last_time

    def terminate(self):
        logger.info(f"Terminating experiment with ID: {getattr(self, 'experiment_id', 'Unknown')}")
        if hasattr(self, 'preparation_future') and self.preparation_future.done():
            self.preparation_future.cancel()
        elif hasattr(self, 'finished_flags') and hasattr(self, 'experiments'):
            for exp_ind, finished in enumerate(self.finished_flags):
                if (not finished) and self.experiments != []:
                    self.experiments[exp_ind].kill()
        if hasattr(self, 'queues'):
            for q in self.queues:
                q.close()

    def __del__(self):
        self.terminate()
