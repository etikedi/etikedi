import random
import pandas as pd
from .active_learning.BaseOracle import BaseOracle


class AergiaOracle(BaseOracle):
    def get_labeled_samples(self, query_indices, data_storage):
        labels = pd.DataFrame(columns=[0], dtype=int)
        for indice in query_indices:
            # note that the result should contain the index - label relation
            labels.loc[indice] = [
                random.randint(0, 2)
            ]  # just return some random labels -> they should be coming from the Aergia Frontend instead!
        return labels
