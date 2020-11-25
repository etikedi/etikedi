import random
import pandas as pd
from ..active_learning.BaseOracle import BaseOracle


class AergiaOracle(BaseOracle):
    def get_labeled_samples(self, query_indices, data_storage):
        labels = []
        for indice in query_indices:
            labels.append(random.randint(0, 2))
        return labels
