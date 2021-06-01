import multiprocessing
from multiprocessing.connection import Connection
from typing import Dict, Optional, List

from .prepare import prepare_dataset_for_active_learning
from ..active_learning.BaseOracle import BaseOracle
from ..active_learning.al_cycle_wrapper import train_al
from ..active_learning.experiment_setup_lib import init_logger
from ..active_learning.dataStorage import DataStorage
from ..config import db, logger
from ..models import Dataset
from .types import *


default_config = {
    "ALLOW_RECOMMENDATIONS_AFTER_STOP": True,
    "AMOUNT_OF_FEATURES": -1,
    "BATCH_MODE": False,
    "CLASSIFIER": "RF",
    "CLUSTER": "dummy",
    "CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE": 0.3,
    "CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED": 0.8,
    "DATASET_NAME": "Trolololo",
    "DISTANCE_METRIC": "euclidean",
    "GENERATE_NOISE": True,
    "HYPERCUBE": True,
    "INITIAL_BATCH_SAMPLING_ARG": 10,
    "INITIAL_BATCH_SAMPLING_HYBRID_FURTHEST": 0.4,
    "INITIAL_BATCH_SAMPLING_HYBRID_FURTHEST_LAB": 0,
    "INITIAL_BATCH_SAMPLING_HYBRID_PRED_UNITY": 0,
    "INITIAL_BATCH_SAMPLING_HYBRID_UNCERT": 0.4,
    "INITIAL_BATCH_SAMPLING_METHOD": "furthest",
    "MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS": 0,
    "NEW_SYNTHETIC_PARAMS": False,
    "NR_LEARNING_ITERATIONS": 200000,
    "NR_QUERIES_PER_ITERATION": 5,
    "N_JOBS": -1,
    "PLOT_EVOLUTION": False,
    "RANDOM_SEED": 10,
    "SAMPLING": "uncertainty_max_margin",
    "STATE_ARGSECOND_PROBAS": True,
    "STATE_ARGTHIRD_PROBAS": True,
    "STATE_DIFF_PROBAS": False,
    "STATE_DISTANCES": False,
    "STATE_DISTANCES_LAB": True,
    "STATE_DISTANCES_UNLAB": True,
    "STATE_INCLUDE_NR_FEATURES": True,
    "STATE_PREDICTED_CLASS": False,
    "STATE_PREDICTED_UNITY": False,
    "STATE_UNCERTAINTIES": False,
    "STOPPING_CRITERIA_ACC": 1.0,
    "STOPPING_CRITERIA_STD": 1.0,
    "STOPPING_CRITERIA_UNCERTAINTY": 1.0,
    "STOP_AFTER_MAXIMUM_ACCURACY_REACHED": False,
    "TEST_FRACTION": 0.3,
    "UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD": 0.99,
    "UNCERTAINTY_RECOMMENDATION_RATIO": 0.01,
    "USER_QUERY_BUDGET_LIMIT": 2000,
    "VARIABLE_DATASET": True,
    "WITH_CLUSTER_RECOMMENDATION": False,
    "WITH_SNUBA_LITE": False,
    "WITH_UNCERTAINTY_RECOMMENDATION": False,
}


class ActiveLearningProcess(multiprocessing.Process, BaseOracle):
    """
    Extension of multiprocessing. Process as a wrapper class for asynchronous execution of active-learning
    code lifecycle.
    """
    dataset_id: int
    # config: ActiveLearningConfig
    config: dict
    pipe_endpoint: Connection
    storage: DataStorage = None

    # Stores information about the samples that currently should get labelled by the user
    current_samples: Dict[SampleID, Optional[LabelID]] = None

    sample_mapping: Dict[SampleID, InternalSampleID]
    reverse_sample_mapping: Dict[InternalSampleID, SampleID]

    def __init__(self, dataset_id: int, config: Dict, pipe_endpoint: Connection):
        super().__init__()
        self.dataset_id = dataset_id
        self.config = config
        self.pipe_endpoint = pipe_endpoint

    def run(self):
        """
        This methods represents the entry point to the active-learning code.
        Before it can be started, data has to get retrieved from database.
        This is done via a member of this class which allows an unambiguously identification of the queried dataset.
        After the data preparation is done, a BaseOracle object is created and - including with the configuration and
        data -  fed to the active learning code.
        """
        init_logger("console")
        logger.info(f'Running worker for dataset {self.dataset_id}')

        self.current_samples = {}

        dataset = db.query(Dataset).filter_by(id=self.dataset_id).first()
        df, self.sample_mapping, self.reverse_sample_mapping = prepare_dataset_for_active_learning(dataset)

        self.config = default_config
        self.config['DATASET_NAME'] = f'Dataset {self.dataset_id}'

        (_, _, metrics_per_al_cycle, data_storage, _) = train_al(
            hyper_parameters=self.config,
            df=df,
            oracle=self
        )
        logger.info(f'Worker for dataset {self.dataset_id} has started')
        self.storage = data_storage

    def label_to_internal_representation(self, label) -> int:
        """
        Returns the internal representation of the given raw label.

        This is needed because the labels have to be converted to integers
        and normalised to start with zero.
        """
        return self.storage.label_encoder.transform([label])[0]

    def is_requested(self, sample_id: SampleID) -> bool:
        """ Checks if the given sample was requested by the AL code. False means, it is a random sample. """
        return sample_id in self.current_samples

    def add_sample(self, sample_id: SampleID, label_id: LabelID):
        logger.debug(f"ALProcess.Oracle:\tFound label {label_id} for sample with id {sample_id}")
        if self.is_requested(sample_id):
            self.current_samples[sample_id] = self.label_to_internal_representation(label_id)
        else:
            # Update will be considered when the classifier is retrained the next time
            internal_sample_id = self.sample_mapping[sample_id]
            internal_label_id = self.label_to_internal_representation(label_id)
            self.storage.update_samples(query_indices=[internal_sample_id], Y_query=[internal_label_id])

    def remove_sample(self, sample_id: int) -> None:
        if self.is_requested(sample_id):
            # Has not been returned so no harm done
            self.current_samples[sample_id] = None
        else:
            # Update will be considered when the classifier is retrained the next time
            self.storage.unlabel_samples([sample_id])

    @property
    def remaining_samples(self) -> List[SampleID]:
        return [sample_id for sample_id, label_id in self.current_samples.items() if label_id is None]

    def new_labels_ordered_by_samples(self, requested_samples: List[SampleID]) -> List[LabelID]:
        return [self.current_samples[sample_id] for sample_id in requested_samples]

    def get_labeled_samples(self, requested_sample_ids: List[InternalSampleID], data_storage: DataStorage, metrics: Dict = None):
        """
        As this function is the only interface between backend and active-learning code, two tasks have to be done:
            1)  Resolving the query indices into queried sample_ids and send them to backend
            2)  Periodical checking for updated labels of queried samples coming from frontend via backend

        To achieve this, a Connection() endpoint is given to this class and the backend respectively, which serves as a
        bidirectional means of communication:

            -   Messages sent by this class represent the datapoints queried by the active-learning code.
            -   Messages received by this class represent updated label data.

        :param requested_sample_ids    indices of data points which have to get labeled by frontend
        :param data_storage            data points the active-learning code was started with
        :return                        List of labels, retrieved from frontend
        """
        self.storage = data_storage

        requested_sample_db_ids = [self.reverse_sample_mapping[raw_id] for raw_id in requested_sample_ids]

        logger.debug(f"ALProcess.Oracle:\tRequesting labels for sample ids: {requested_sample_db_ids}")

        self.current_samples = {sample_id: None for sample_id in requested_sample_db_ids}
        self.pipe_endpoint.send({
            'event': 'request_samples',
            'sample_ids': [int(sample_id) for sample_id in requested_sample_db_ids],
            'metrics': metrics
        })

        while self.remaining_samples:
            self.pipe_endpoint.poll(None)  # Infinite timeout
            message = self.pipe_endpoint.recv()

            if message['event'] == 'add_sample':
                self.add_sample(sample_id=message['sample_id'], label_id=message['label_id'])

            if message['event'] == 'remove_sample':
                self.remove_sample(sample_id=message['sample_id'])

            if self.remaining_samples:
                logger.debug(f"ALProcess.Oracle:\tWaiting for remaining labels of samples {self.remaining_samples}")

        logger.debug("ALProcess.Oracle:\tRequested labels complete. Current iteration successfully terminated")
        return self.new_labels_ordered_by_samples(requested_sample_db_ids)
