import random
from ..active_learning.BaseOracle import BaseOracle


class EtikediOracle(BaseOracle):
    def get_labeled_samples(self, query_indices, data_storage):
        labels = []
        for _ in query_indices:
            labels.append(random.randint(0, 2))
        return labels
