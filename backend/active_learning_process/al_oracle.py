from typing import Dict

from multiprocessing.connection import Connection
from sklearn.preprocessing import LabelEncoder
import numpy as np

from ..active_learning.BaseOracle import BaseOracle
from ..config import logger


class ParallelOracle(BaseOracle):
    """
    Extension of base class BaseOracle of active_learning submodule.

    Enables communication between backend and the corresponding active-learning process via usage of
    multiprocessing.Pipe(), which creates two socket-like endpoints. One is stored by the ProcessManager object and
    one is a member of this class.
    """

    def __init__(
        self,
        sample_ids: Dict[int, int],
        pipe_endpoint: Connection,
        label_encoder: LabelEncoder,
    ):
        self.sample_ids = sample_ids
        self.pipe_endpoint = pipe_endpoint
        self.label_encoder = label_encoder

    def label_to_internal_representation(self, label) -> int:
        """
        Returns the internal representation of the given raw label.

        This is needed because the labels have to be converted to integers
        and normalised to start with zero.
        """
        return self.label_encoder.transform([label])[0]

    def get_labels(self, requested_sample_ids, data_storage):
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
        for sample_id in requested_sample_ids:
            self.pipe_endpoint.send(int(sample_id))

        logger.debug(
            "ALProcess.Oracle:\tRequesting labels for sample ids: "
            + str(requested_sample_ids)
        )
        remaining_sample_ids = requested_sample_ids.copy()
        labels_by_query_index = {}
        while len(requested_sample_ids) is not len(labels_by_query_index):
            if self.pipe_endpoint.poll():
                data = self.pipe_endpoint.recv()
                logger.debug(
                    "ALProcess.Oracle:\tFound label "
                    + str(data["label"])
                    + " for sample with id "
                    + str(data["id"])
                )

                position = np.where(requested_sample_ids == data["id"])[0][0]
                labels_by_query_index[position] = self.label_to_internal_representation(
                    data["label"]
                )

                position = np.where(remaining_sample_ids == data["id"])[0][0]
                remaining_sample_ids = np.delete(remaining_sample_ids, position)
                if len(remaining_sample_ids) != 0:
                    logger.debug(
                        "ALProcess.Oracle:\tWaiting for remaining labels of samples "
                        + str(remaining_sample_ids)
                    )
        logger.debug(
            "ALProcess.Oracle:\tRequested labels complete. Current iteration successfully terminated"
        )
        labels = [labels_by_query_index[i] for i in range(len(requested_sample_ids))]
        return labels
