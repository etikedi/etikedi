from multiprocessing import Pipe

from active_learning_process.al_process import ALProcess


class ProcessManager:

    def __init__(self):
        self.queues_of_process_by_dataset_id = {}

    def get_or_else_load(self, dataset_id):
        if dataset_id in self.queues_of_process_by_dataset_id:
            print("ProcessManager:\tProcess for this dataset " + str(dataset_id) + " already running")
            return self.queues_of_process_by_dataset_id[dataset_id]
        else:
            print("ProcessManager:\tStarting new process for dataset " + str(dataset_id))
            backend_endpoint, process_endpoint = Pipe()
            new_process = ALProcess(dataset_id, process_endpoint)
            new_process.start()
            self.queues_of_process_by_dataset_id[dataset_id] = backend_endpoint
            return self.queues_of_process_by_dataset_id[dataset_id]

