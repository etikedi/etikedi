from active_learning.BaseOracle import BaseOracle


class ParallelOracle(BaseOracle):

    def __init__(self, sample_ids, to_label_queue, label_queue):
        self.sample_ids = sample_ids
        self.to_label_queue = to_label_queue
        self.label_queue = label_queue

    def get_labels(self, query_indices, data_storage):
        query_sample_ids = [self.sample_ids[index] for index in tuple(query_indices)]
        self.to_label_queue.put(query_sample_ids)
        print("Requesting labels for sample ids: " + str(query_sample_ids))
        remaining_sample_ids = query_sample_ids.copy()
        labels_by_query_index = {}
        while len(query_indices) is not len(labels_by_query_index):
            if not self.label_queue.empty():
                data = self.label_queue.get()
                print("Found label " + str(data["label"]) + " for sample with id " + str(data["id"]))
                position = query_sample_ids.index(data["id"])
                labels_by_query_index[position] = data["label"]
                remaining_sample_ids.remove(data["id"])
                if len(remaining_sample_ids) != 0:
                    print("Waiting for remaining labels of samples " + str(remaining_sample_ids))
        print("Requested labels complete. Current iteration successfully terminated")
        labels = [labels_by_query_index[i] for i in range(len(query_indices))]
        return labels