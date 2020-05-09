import random
import time

import pandas as pd

from active_learning.BaseOracle import BaseOracle


class ParallelOracle(BaseOracle):

    def get_labels(self, query_indices, data_storage):
        print("Oracle: " + str(query_indices))
        # insert toBeLabeled into Database

        # for item in query_indices:
        #   INSERT INTO label_queue (id) values (item);
        labels = pd.DataFrame(columns=[0], dtype=int)
        while len(query_indices) is not len(labels):
            print("Checking for new labels")
            # for indice in query_indices:
            #     sample = self.samples[indice]
            #     label = Association.query.filter_by(sample_id=sample.id)
            #     if label is not None:
            #         labels.append(label)
            #     else:
            #         break
            time.sleep(5)
        print("Successfully terminated iteration")
        return labels
