import random
import time

import pandas as pd

from backend.active_learning.BaseOracle import BaseOracle
from backend.models import Association
from backend.models.label_queue import LabelQueue
from ..aergia import db

class ParallelOracle(BaseOracle):

    def __init__(self, sample_ids):
        self.sample_ids = sample_ids

    def get_labels(self, query_indices, data_storage):
        print("Oracle: " + str(query_indices))
        # insert toBeLabeled into Database
        query_sample_ids = [self.sample_ids[indice] for indice in query_indices]
        for sample_id in query_sample_ids:
            db.session.add(LabelQueue(sample_id))
        db.session.commit()
        labels = pd.DataFrame(columns=[0], dtype=int)
        while len(query_indices) is not len(labels):
            print("Checking for new labels")
            for sample_id in query_sample_ids:
                label = Association.query.filter_by(sample_id=sample_id)
                if label is not None:
                    labels.append(label)
                else:
                    break
            time.sleep(5)
        print("Successfully terminated iteration")
        for sample_id in query_sample_ids:
            LabelQueue.query.filter_by(id=sample_id).delete()
        db.session.commit()
        return labels
