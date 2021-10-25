import multiprocessing
import random
import time
import numpy as np
from enum import Enum
from multiprocessing.connection import Connection
from typing import List, Tuple

from alipy import metrics
from alipy.index import IndexCollection

from .etiTypes import *
from ..config import db, logger
from ..models import Dataset, Sample, QueryStrategyAbstraction, ActiveLearningConfig


class EventType(Enum):
    ADD = 0,
    REMOVE = 1,
    REQUEST = 2,
    STOP = 3,


def split_by_pred(pred: callable, list: List) -> Tuple[List, List]:
    l1 = []
    l2 = []
    for item in list:
        if pred(item):
            l1.append(item)
        else:
            l2.append(item)
    return l1, l2


class ActiveLearningProcess(multiprocessing.Process):
    """
    Extension of multiprocessing. Process as a wrapper class for asynchronous execution of active-learning
    code lifecycle.
    """
    dataset_id: int
    # config: ActiveLearningConfig
    config: ActiveLearningConfig
    pipe_endpoint: Connection

    def __init__(self, dataset_id: int, pipe_endpoint: Connection):
        super().__init__()
        self.dataset_id = dataset_id
        self.pipe_endpoint = pipe_endpoint
        # everything heavy is done async to keep the main thread clean

    def _prepare(self):
        dataset: Dataset = db.get(Dataset, self.dataset_id)
        self.config = dataset.get_config()
        # split samples
        unlabeled, labeled = split_by_pred(lambda smpl: smpl.labels == [], dataset.samples)

        # TODO use configuration
        nbr_of_samples = len(dataset.samples)
        nbr_of_features = len(dataset.feature_names.split(","))

        self.idx_sample_map = {}
        self.sample_idx_map = {}
        complete_feature_matrix = np.empty((nbr_of_samples, nbr_of_features))  # empty 2d array
        for idx, sample in enumerate(dataset.samples):
            complete_feature_matrix[idx] = sample.extract_feature_list()
            self.idx_sample_map[idx] = sample.id
            self.sample_idx_map[sample.id] = idx

        # assuming dataset is single labeled
        label_list = np.empty(shape=nbr_of_samples, dtype=str)
        for lab_sample in labeled:
            label_list[self.sample_idx_map[lab_sample.id]] = lab_sample.labels[0].name
        # create index collection and query
        self.unlabeled_idx = IndexCollection([self.sample_idx_map[sample.id] for sample in unlabeled])
        self.labeled_idx = IndexCollection([self.sample_idx_map[sample.id] for sample in labeled])
        self.query_strategy = QueryStrategyAbstraction.build(qs_type=self.config.QUERY_STRATEGY,
                                                               X=complete_feature_matrix,
                                                               y=label_list,
                                                               config=self.config.QUERY_STRATEGY_CONFIG,)
        model_class = self.config.AL_MODEL.get_class()
        self.model = model_class()
        self.batch_size = self.config.BATCH_SIZE
        self.counter_until_next_eval = self.config.COUNTER_UNTIL_NEXT_EVAL
        self.counter_until_next_update = self.config.COUNTER_UNTIL_NEXT_MODEL_UPDATE
        self.evaluation_size = 30  # number of samples used to measure prediction

    def run(self):
        """
        This methods represents the entry point to the active-learning code.
        Before it can be started, data has to get retrieved from database.
        This is done via a member of this class which allows an unambiguously identification of the queried dataset.
        After the data preparation is done, a BaseOracle object is created and - including with the configuration and
        data -  fed to the active learning code.
        """
        print(f'Running process for dataset {self.dataset_id}')
        self._prepare()
        self._update_model(bypass_counter=True)
        self._wait_for_events()

    def _wait_for_events(self):
        """
        As this function is the only interface between backend and active-learning code, two tasks have to be done:
            1)  Resolving the query indices into queried sample_ids and send them to backend
            2)  Periodical checking for updated labels of queried samples coming from frontend via backend

        To achieve this, a Connection() endpoint is given to this class and the backend respectively, which serves as a
        bidirectional means of communication:

            -   Messages sent by this class represent the datapoints queried by the active-learning code.
            -   Messages received by this class represent updated label data.
        """
        while True:
            print(f'WorkerID: {self.dataset_id} waiting for events')
            self.pipe_endpoint.poll(None)  # Infinite timeout
            message = self.pipe_endpoint.recv()

            event_type = message['event']
            print(f"workerID: {self.dataset_id} Received event{event_type}")

            if event_type == EventType.ADD:
                self.add_label(sample_id=message['sample_id'])

            elif event_type == EventType.REMOVE:
                self.remove_label(sample_id=message['sample_id'])

            elif event_type == EventType.REQUEST:
                print(f"WorkerID: {self.dataset_id} sending response")
                assert not self.pipe_endpoint.closed
                assert self.pipe_endpoint.writable
                self.pipe_endpoint.send({
                    'event': EventType.REQUEST,
                    'sample_ids': self._request_next_sample(),
                })
            elif event_type == EventType.STOP:
                break

        exit()

    def add_label(self, sample_id: SampleID):
        idx = self.sample_idx_map[sample_id]
        self.labeled_idx.update(idx)
        self.unlabeled_idx.difference_update(idx)
        self._update_model()

    def remove_label(self, sample_id: int) -> None:
        idx = self.sample_idx_map[sample_id]
        self.labeled_idx.difference_update(idx)
        self.unlabeled_idx.update(idx)
        self._update_model(measure=False)

    def _update_model(self, measure=True, bypass_counter=False):
        if not bypass_counter:
            self.counter_until_next_update -= 1
            if self.counter_until_next_update > 0:
                return
            # reset counter and update model
            self.counter_until_next_update = self.batch_size
        if measure:
            self._measure_model()

    def _measure_model(self):
        print("Starting model training")
        dataset: Dataset = db.query(Dataset).get(self.dataset_id)
        labeled_samples: List[Sample] = list(filter(lambda smpl: smpl.labels != [], dataset.samples))

        # extract features from json
        X = []  # feature_matrix: 2d list
        y = []  # label_list: 1d list
        for sample in labeled_samples:
            X.append(sample.extract_feature_list())
            y.append(sample.labels[0].name)  # assuming dataset is single-labeled
        start = time.time()
        try:
            self.model.fit(X, y)
        except Exception as e:
            logger.error(e)
            return
        finally:
            stop = time.time()
            print(f"Training phase took: {round(stop - start, 3)}s")

        # reset counter and measure accuracy
        rand_test_sample_list: List[Sample] = [random.choice(labeled_samples) for _ in range(30)]
        label = [sample.labels[0].name for sample in rand_test_sample_list]
        predictions = self.model.predict([sample.extract_feature_list() for sample in rand_test_sample_list])
        accuracy = metrics.accuracy_score(predictions, label)
        labeled_percentage = len(labeled_samples) / len(dataset.samples)
        # TODO save prediction history
        print(f"prediction accuracy: {round(accuracy * 100, 2)}%,"
              f" with {round(labeled_percentage * 100, 2)}% labeled dataset")

    def _request_next_sample(self) -> List[int]:

        selected_id_list: List = self.query_strategy.select(label_index=self.labeled_idx,
                                                            unlabel_index=self.unlabeled_idx,
                                                            model=self.model, batch_size=self.batch_size)
        # only work with ids to reduce db-access times
        selected_sample_ids: List[int] = [self.idx_sample_map[sel_id] for sel_id in selected_id_list]
        return selected_sample_ids
