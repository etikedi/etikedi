import json
from datetime import datetime, timedelta
from enum import Enum
from multiprocessing import Pipe
from multiprocessing.connection import Connection
from sqlalchemy import func as db_functions
from typing import Dict, Union

from .process import ActiveLearningProcess
from ..config import db
from ..models import Dataset, Sample, ActiveLearningConfig


class WorkerState(Enum):
    TRAINING = 'training'
    WAITING = 'waiting'
    STARTING = 'starting'


class ActiveLearningWorker:
    dataset: Dataset
    config: ActiveLearningConfig
    process: ActiveLearningProcess
    pipe: Connection
    state: WorkerState

    # The values are the time the sample was sent to a user
    requested_samples: Dict[int, Union[datetime, None]]

    # Time the user has to label before sample gets unlocked
    # TODO: Refactor to config option
    user_time_to_label = timedelta(seconds=30)

    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.create_process()
        self.start_process()

        self.requested_samples = {}
        self.config = dataset.get_config()

    def create_process(self) -> None:
        self.pipe, other_endpoint = Pipe(duplex=True)
        self.process = ActiveLearningProcess(
            dataset_id=self.dataset.id,
            config=json.loads(self.dataset.config),
            pipe_endpoint=other_endpoint
        )

    def start_process(self) -> None:
        self.process.start()
        self.state = WorkerState.TRAINING

    def restart_process(self, config: ActiveLearningConfig) -> None:
        """
        Restarts the current running active-learning process for the specified data set with the given configuration
        returns the new process' resources. Resources being the process object itself and the corresponding pipe
        backend endpoint for communication with said process.

        If there's currently no process running for the given data set id, a new one is created and its resources
        are returned.

        :param config:      configuration for active-learning code the process is restarted with
        """
        self.state = WorkerState.STARTING
        if self.process.is_alive():
            self.process.kill()
        del self.process
        self.config = config
        self.create_process()
        self.start_process()

    def __del__(self):
        self.process.kill()

    def add_sample_label(self, sample_id: int, label_id: int) -> None:
        if sample_id in self.requested_samples:
            del self.requested_samples[sample_id]

        self.pipe.send({
            "event": "add_sample",
            "sample_id": sample_id,
            "label_id": label_id
        })

        if len(self.requested_samples.keys()) == 0:
            self.state = WorkerState.TRAINING

    def remove_sample_label(self, sample_id: int, label_id) -> None:
        self.pipe.send({
            "event": "remove_sample",
            "sample_id": sample_id,
            "label_id": label_id
        })

    def get_next_sample(self) -> Sample:
        self.check_still_training()
        if self.state is WorkerState.TRAINING:
            return self.get_random_unlabelled_sample()
        if self.state is WorkerState.WAITING:
            return self.get_requested_sample()
        raise RuntimeError('Unable to handle current worker state')

    def check_still_training(self) -> None:
        if self.state == WorkerState.TRAINING and self.pipe.poll():
            # Check if its done training
            message = self.pipe.recv()
            if message['event'] != 'request_samples':
                raise RuntimeError('No idea what to do next')

            self.requested_samples = {sample_id: None for sample_id in message['sample_ids']}
            self.state = WorkerState.WAITING

    def get_requested_sample(self) -> Sample:
        self.unlock_samples()

        sample_id = next(sample_id for sample_id, sent_to_user in self.requested_samples.items() if sent_to_user is None)
        self.requested_samples[sample_id] = datetime.now()

        return db.query(Sample).filter(Sample.id == sample_id).first()

    def get_random_unlabelled_sample(self) -> Sample:
        return db.query(Sample) \
            .filter(Sample.dataset == self.dataset, ~Sample.associations.any()) \
            .order_by(db_functions.random()) \
            .first()

    def unlock_samples(self):
        """ Unlocks all samples which where sent to user but not labelled in time. """
        now = datetime.now()

        for sample_id, sent_to_user in self.requested_samples.items():
            if not sent_to_user:
                continue

            if sent_to_user + self.user_time_to_label <= now:
                difference = now - sent_to_user
                print(f'Unlock requested sample {sample_id} for dataset {self.dataset} as it was '
                      f'sent to a user {difference.total_seconds()} ago')
                self.requested_samples[sample_id] = None

        # Shorter version without logging
        # self.requested_samples = {
        #     sample_id: sent_to_user if sent_to_user + self.user_time_to_label >= now else None
        #     for sample_id, sent_to_user in self.requested_samples.items()
        # }
