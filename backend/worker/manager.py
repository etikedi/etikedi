import time
from typing import Dict, Optional

from ..models import Dataset
from .alWorker import AlWorker


class ProcessManager:
    """
    Class for management of active-learning process for different data sets.
    """
    workers: Dict[int, AlWorker] = {}

    def get_or_else_load(self, dataset: Dataset) -> AlWorker:
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
            return self.create_worker(dataset.id)

    def get(self, dataset: Dataset) -> Optional[AlWorker]:
        return self.workers.get(dataset.id)

    def create_worker(self, dataset_id: int) -> AlWorker:
        worker = AlWorker(dataset_id)
        self.workers[dataset_id] = worker
        return worker


manager = ProcessManager()
