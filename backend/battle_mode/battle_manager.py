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
    BattleMetaActive,
    ExperimentQueueEvent,
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
    def get_all_active_finished() -> Dict[int, BattleMetaActive]:
        loaded_battle: Dict[int, BattleMetaActive] = {}
        for experiment_id, battle in BattleManager._manager.items():
            loaded_battle[experiment_id] = BattleMetaActive(
                experiment_id=experiment_id,
                config=battle.config,
                dataset_id=battle.dataset_id,
                status=battle.update_and_get_state()
            )
        for experiment_id, finished in BattleManager._finished_manager.items():
            loaded_battle[experiment_id] = BattleMetaActive(
                experiment_id=experiment_id,
                config=finished.config,
                dataset_id=finished.dataset_id,
                status=Status(code=Status.Code.COMPLETED)
            )
        return loaded_battle

    @staticmethod
    def get_status_for_active(experiment_id: int) -> Status:
        battle = BattleManager._manager[experiment_id]
        state = battle.update_and_get_state()
        if state.code == Status.Code.FAILED and not battle.is_terminated():
            BattleManager._manager[experiment_id].terminate()
        return state

    @staticmethod
    def assert_experiment_finished(experiment_id: int):
        if BattleManager.get_status_for_active(experiment_id).code != Status.Code.COMPLETED:
            raise ValidationError("Experiment is not finished: " + str(experiment_id))

    @staticmethod
    def set_finished_manager(manager: BattleAnalyzer):
        if manager.experiment_id in BattleManager._finished_manager:
            logger.warn("Replacing finished existing manager for id: " + str(manager.experiment_id))
        BattleManager._finished_manager[manager.experiment_id] = manager

    @staticmethod
    def get_or_create_finished_manager(experiment_id: int) -> BattleAnalyzer:
        if experiment_id not in BattleManager._finished_manager:
            battle = BattleManager._manager[experiment_id]
            BattleManager.assert_experiment_finished(experiment_id)
            if any(r is None for r in battle.results):
                logger.error(f"Battle {experiment_id} is supposed to be finished but has no results.")
                battle.terminate()

            manager = BattleAnalyzer(
                experiment_id=experiment_id,
                dataset_id=battle.dataset_id,
                config=battle.config,
                cb_sample=battle.cb_sample,
                result_one=battle.results[0],
                result_two=battle.results[1])
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
        self.experiment_states: List[Status, Status] = [Status(code=Status.Code.IN_SETUP) for _ in [0, 1]]
        self.results: List[Optional[ExperimentResults], Optional[ExperimentResults]] = [None, None]
        self.metric: Optional[Metric] = None
        self.queues = [Queue(), Queue()]
        self._is_terminated = False
        # initialized in callback
        self.cb_sample: Optional[pd.DataFrame] = None  # generated samples for classification boundaries
        self.experiments: Tuple[ALExperimentProcess] = tuple()  # both processes running the experiments
        self.preparation_future: Optional[Future] = None  # waiting for async preparation
        try:
            self._prepare()
        except Exception as e:
            logger.error(f"Failed battle preparation for id: {self.experiment_id} with error \n: {repr(e)}")
            self._set_failed(repr(e))

    def _prepare(self):
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
            ALExperimentProcess(i, sample_df, self.config, self.queues[i], cb_sample) for i in [0, 1]])
        for exp in self.experiments:
            exp.start()
        logger.info("Started experiments for ID: " + str(self.experiment_id))

    def update_and_get_state(self) -> Status:
        """ @return a [Status] object reflecting the current battle-status.
                0 if still in setup-phase (dataset-preparation or process in setup)
                1 if experiment-processes are running
                2 if finished with time in seconds if at least one has reported something
                """
        last_reported = self._most_significant_state(self.experiment_states)
        if last_reported.code in [Status.Code.FAILED, Status.Code.COMPLETED]:
            return last_reported
        if not self.preparation_future.done():  # preparation callback not finished
            return Status(code=Status.Code.IN_SETUP)

        new_states = [self._poll_process(i) for i in [0, 1]]
        for idx, new_state in enumerate(new_states):
            # don't replace with None
            # or both new and old are training but new is missing time
            if (new_state is None
                    or (new_state.code == Status.Code.TRAINING
                        and self.experiment_states[idx].code == Status.Code.TRAINING
                        and new_state.time is None
                    )):
                continue
            self.experiment_states[idx] = new_state

        return self._most_significant_state(self.experiment_states)

    def _poll_process(self, exp_idx: int) -> Optional[Status]:
        """
        @param exp_idx the queue of experiment one or two
        @return the most important status update or
                None if nothing new was reported
        """
        queue = self.queues[exp_idx]
        status = self.experiment_states[exp_idx]
        if queue.empty():
            return None
        while not queue.empty():
            event: ExperimentQueueEvent = queue.get_nowait()
            if event.event_type == ExperimentQueueEventType.INFO:
                if status.code == Status.Code.TRAINING:
                    status.time = event.value
            elif event.event_type == ExperimentQueueEventType.SETUP_COMPLETED:
                if status.code == Status.Code.IN_SETUP:
                    status = Status(code=Status.Code.TRAINING)
            elif event.event_type == ExperimentQueueEventType.RESULT:
                self.results[exp_idx] = event.value
                self.experiments[exp_idx].join()
                status = Status(code=Status.Code.COMPLETED)
            elif event.event_type == ExperimentQueueEventType.FAILED:
                return Status(code=Status.Code.FAILED, error=event.value)
        return status

    def _set_failed(self, error: str):
        self.experiment_states = [Status(code=Status.Code.FAILED, error=error) for _ in [0, 1]]

    def terminate(self):
        if getattr(self, '_is_terminated', True):
            logger.warn(
                f"Trying to terminate already terminated battle with ID: {getattr(self, 'experiment_id', 'Unknown')}")
            return
        logger.info(f"Terminating experiment with ID: {getattr(self, 'experiment_id', 'Unknown')}")
        if hasattr(self, 'preparation_future') and not self.preparation_future.done():
            self.preparation_future.remove_done_callback(self._start_battle)
            self.preparation_future.cancel()
        elif hasattr(self, 'experiments'):
            for experiment in self.experiments:
                if experiment.is_alive():
                    experiment.kill()
        if hasattr(self, 'queues'):
            for q in self.queues:
                q.close()
        self._set_failed("Battle was terminated")  # further accesses should fail
        self._is_terminated = True

    def is_terminated(self):
        return self._is_terminated if hasattr(self, '_is_terminated') else True

    def __del__(self):
        if not getattr(self, '_is_terminated', True):
            self.terminate()

    @staticmethod
    def _most_significant_state(states: List[Status]) -> Status:
        if any(state.code == Status.Code.FAILED for state in states):
            return next(state for state in states if state.code == Status.Code.FAILED)
        if all(state.code == Status.Code.COMPLETED for state in states):
            return states[0]
        if any(state.code == Status.Code.IN_SETUP for state in states):
            return next(state for state in states if state.code == Status.Code.IN_SETUP)
        # at least one is training the other could be finished or training
        times = [state.time for state in states if state.time is not None]
        max_time = max(times, default=None)
        return Status(code=Status.Code.TRAINING, time=max_time)
