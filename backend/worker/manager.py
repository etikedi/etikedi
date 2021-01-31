from typing import Dict, Optional

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

    def get(self, dataset: Dataset) -> Optional[ActiveLearningWorker]:
        return self.workers.get(dataset.id)

    def create_worker(self, dataset: Dataset) -> ActiveLearningWorker:
        worker = ActiveLearningWorker(dataset)
        self.workers[dataset.id] = worker
        return worker


manager = ProcessManager()
