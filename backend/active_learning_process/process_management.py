import time
from multiprocessing import Pipe

from . import al_config
from .al_process import ALProcess
from ..config import app


class ProcessManager:
    """
    Class for management of active-learning process for different data sets.
    """
    def __init__(self):
        self.process_resources_by_dataset_id = {}

    def get_or_else_load(self, dataset_id):
        """
        Retrieves resources of an active-learning process for the specified data set id. Resources being the process
        object itself and the corresponding pipe backend endpoint for communication with said process.

        Behaves like the get() function of a loading cache. It is checked whether resources of a process with the
        specified data set id exist. If any are found, they are returned in a dictionary. If none are found, a new
        process is started and its resources are returned.

        :param dataset_id:  ID of data set
        :return:            Process resources as a dictionary with the fields: 'process' and 'pipe'
        """
        if dataset_id in self.process_resources_by_dataset_id:
            app.logger.debug("Backend.ProcessManager:\tProcess for this dataset {} already running".format(dataset_id))
            return self.process_resources_by_dataset_id[dataset_id]
        else:
            app.logger.debug("Backend.ProcessManager:\tStarting new process for dataset {}".format(dataset_id))
            backend_endpoint, process_endpoint = Pipe()
            new_process = ALProcess(al_config.config().__dict__, dataset_id, process_endpoint)
            new_process.start()
            self.process_resources_by_dataset_id[dataset_id] = {"process": new_process, "pipe": backend_endpoint}
            # Wait for active-learning code to finish initializing?
            time.sleep(5)
            return self.process_resources_by_dataset_id[dataset_id]

    def restart_with_config(self, dataset_id, config):
        """
        Restarts the current running active-learning process for the specified data set with the given configuration
        returns the new process' resources. Resources being the process object itself and the corresponding pipe
        backend endpoint for communication with said process.

        If there's currently no process running for the given data set id, a new one is created and its resources
        are returned.

        :param dataset_id:  ID of data set
        :param config:      configuration for active-learning code the process is restarted with
        """
        backend_endpoint, process_endpoint = Pipe()
        new_process = ALProcess(config, dataset_id, process_endpoint)
        if dataset_id in self.process_resources_by_dataset_id:
            old_process = self.process_resources_by_dataset_id[dataset_id]["process"]
            app.logger.debug("Backend.ProcessManager:\tRestarting process for dataset {} with new configuration".format(dataset_id))
            new_process.start()
            self.process_resources_by_dataset_id[dataset_id] = {"process": new_process, "pipe": backend_endpoint}
            old_process.terminate()
            return self.process_resources_by_dataset_id[dataset_id]
        else:
            app.logger.debug("Backend.ProcessManager:\tStarting process for dataset {} with new configuration".format(dataset_id))
            new_process.start()
            self.process_resources_by_dataset_id[dataset_id] = {"process": new_process, "pipe": backend_endpoint}
            return self.process_resources_by_dataset_id[dataset_id]


manager = ProcessManager()
