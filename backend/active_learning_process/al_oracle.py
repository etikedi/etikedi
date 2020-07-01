from ..active_learning.BaseOracle import BaseOracle
from ..config import app


class ParallelOracle(BaseOracle):
    """
    Extension of base class BaseOracle of active_learning submodule.

    Enables communication between backend and the corresponding active-learning process via usage of
    multiprocessing.Pipe(), which creates two socket-like endpoints. One is stored by the ProcessManager object and
    one is a member of this class.
    """

    def __init__(self, sample_ids, pipe_endpoint):
        self.sample_ids = sample_ids
        self.pipe_endpoint = pipe_endpoint

    def get_labels(self, query_indices, data_storage):
        """
        As this function is the only interface between backend and active-learning code, two tasks have to be done:
            1)  Resolving the query indices into queried sample_ids and send them to backend
            2)  Periodical checking for updated labels of queried samples coming from frontend via backend

        To achieve this, a Connection() endpoint is given to this class and the backend respectively, which serves as a
        bidirectional means of communication:

            -   Messages sent by this class represent the datapoints queried by the active-learning code.
            -   Messages received by this class represent updated label data.

        :param query_indices    indices of data points which have to get labeled by frontend
        :param data_storage     data points the active-learning code was started with
        :return:                List of labels, retrieved from frontend
        """
        query_sample_ids = [self.sample_ids[index] for index in tuple(query_indices)]
        for sample_id in query_sample_ids:
            self.pipe_endpoint.send(sample_id)
        app.logger.debug("ALProcess.Oracle:\tRequesting labels for sample ids: " + str(query_sample_ids))
        remaining_sample_ids = query_sample_ids.copy()
        labels_by_query_index = {}
        while len(query_indices) is not len(labels_by_query_index):
            if self.pipe_endpoint.poll():
                data = self.pipe_endpoint.recv()
                app.logger.debug("ALProcess.Oracle:\tFound label " + str(data["label"]) + " for sample with id " + str(data["id"]))
                position = query_sample_ids.index(data["id"])
                labels_by_query_index[position] = data["label"]
                remaining_sample_ids.remove(data["id"])
                if len(remaining_sample_ids) != 0:
                    app.logger.debug("ALProcess.Oracle:\tWaiting for remaining labels of samples " + str(remaining_sample_ids))
        app.logger.debug("ALProcess.Oracle:\tRequested labels complete. Current iteration successfully terminated")
        labels = [labels_by_query_index[i] for i in range(len(query_indices))]
        return labels

