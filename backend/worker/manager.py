from multiprocessing import Pipe
from typing import Dict

from ..config import logger
from ..models import Dataset
from .worker import ActiveLearningWorker


class ProcessManager:
    """
    Class for management of active-learning process for different data sets.
    """
    workers: Dict[int, ActiveLearningWorker] = {}

    def get_or_else_load(self, dataset: Dataset) -> ActiveLearningWorker:
        """
        Retrieves resources of an active-learning process for the specified data set id. Resources being the process
        object itself and the corresponding pipe backend endpoint for communication with said process.

        Behaves like the get() function of a loading cache. It is checked whether resources of a process with the
        specified data set id exist. If any are found, they are returned in a dictionary. If none are found, a new
        process is started and its resources are returned.

        :return:            Process resources as a dictionary with the fields: 'process' and 'pipe'
        """
        if dataset.id in self.workers:
            return self.workers[dataset.id]
        else:
            return self.create_worker(dataset)

    def create_worker(self, dataset: Dataset) -> ActiveLearningWorker:
        worker = ActiveLearningWorker(dataset)
        self.workers[dataset.id] = worker
        return worker
        # logger.debug("Starting new process for dataset {}".format(dataset))
        # backend_endpoint, process_endpoint = Pipe()
        # new_process = ALProcess(
        #     json.loads(dataset.config), dataset.id, process_endpoint
        # )
        # new_process.start()
        # self.process_resources_by_dataset_id[dataset.id] = ProcessEntry(
        #     process=new_process,
        #     pipe=backend_endpoint
        # )
        # return self.process_resources_by_dataset_id[dataset.id]

    def restart_with_config(self, dataset: Dataset, config: dict):
        """
        Restarts the current running active-learning process for the specified data set with the given configuration
        returns the new process' resources. Resources being the process object itself and the corresponding pipe
        backend endpoint for communication with said process.

        If there's currently no process running for the given data set id, a new one is created and its resources
        are returned.

        :param dataset:
        :param config:      configuration for active-learning code the process is restarted with
        """
        raise RuntimeError("Not yet implemented. Wait for update")
        # backend_endpoint, process_endpoint = Pipe()
        # new_process = ALProcess(config, dataset.id, process_endpoint)
        # if dataset.id in self.process_resources_by_dataset_id:
        #     old_process = self.process_resources_by_dataset_id[dataset.id].process
        #     old_process.terminate()
        #     logger.debug(
        #         "Restarting process for dataset {} with new configuration".format(
        #             dataset.id
        #         )
        #     )
        #     new_process.start()
        #     self.process_resources_by_dataset_id[dataset.id] = ProcessEntry(
        #         process=new_process,
        #         pipe=backend_endpoint
        #     )
        #     return self.process_resources_by_dataset_id[dataset.id]
        # else:
        #     logger.debug(
        #         "Starting process for dataset {} with new configuration".format(
        #             dataset.id
        #         )
        #     )
        #     new_process.start()
        #     self.process_resources_by_dataset_id[dataset.id] = ProcessEntry(
        #         process=new_process,
        #         pipe=backend_endpoint
        #     )
        #     return self.process_resources_by_dataset_id[dataset.id]


manager = ProcessManager()
