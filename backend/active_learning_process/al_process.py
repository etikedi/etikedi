import multiprocessing
from io import StringIO

import numpy as np
import pandas as pd
from fastapi import Depends
from sklearn.preprocessing import LabelEncoder
from sqlalchemy.orm import Session

from .al_oracle import ParallelOracle
from ..active_learning.al_cycle_wrapper import train_al
from ..active_learning.experiment_setup_lib import init_logger
from ..config import logger, get_db
from ..models import Association, Sample, Dataset


class ALProcess(multiprocessing.Process):
    """
    Extension of multiprocessing. Process as a wrapper class for asynchronous execution of active-learning
    code lifecycle.
    """

    def __init__(self, config, dataset_id: int, pipe_endpoint):
        super().__init__()
        self.dataset_id = dataset_id
        self.config = config
        self.pipe_endpoint = pipe_endpoint

    def run(self, db: Session = Depends(get_db)):
        """
        This methods represents the entry point to the active-learning code.
        Before it can be started, data has to get retrieved from database.
        This is done via a member of this class which allows an unambiguously identification of the queried dataset.
        After the data preparation is done, a BaseOracle object is created and - including with the configuration and
        data -  fed to the active learning code.
        """
        init_logger("log.txt")
        dataset = Dataset.query.get(self.dataset_id)
        logger.info("Starting for dataset {}".format(self.dataset_id))

        buffer = StringIO(dataset.features)
        sample_df = pd.read_csv(buffer).set_index("ID")
        sample_ids = dict(enumerate(sample_df.index))

        associated_labels = (
            db.query(Association.sample_id, Association.label_id)
            .join(Association.sample)
            .filter(Sample.dataset == dataset)
            .all()
        )

        label_df = pd.DataFrame(associated_labels, columns=["ID", 0]).set_index("ID")
        label_encoder = LabelEncoder()
        label_encoder.fit(label_df[0].unique())
        label_df[0] = label_encoder.transform(label_df[0])  # Labels now start with 0
        ids_of_labeled_samples = np.array(associated_labels)[:, 0]

        all_sample_ids = (
            db.query(Sample.id)
            .filter(Sample.dataset_id == self.dataset_id)
            .all()
        )
        all_sample_ids = np.array(all_sample_ids)[:, 0]
        sample_df.index = pd.Int64Index(all_sample_ids)

        labeled_sample_df = sample_df.loc[ids_of_labeled_samples]
        unlabeled_sample_df = sample_df.drop(ids_of_labeled_samples)

        # Y_train are the resulting labels
        # metrics_per_al_cycle contains a lot of labels useful for visualisation
        (_, Y_train, _, metrics_per_al_cycle, _, _) = train_al(
            X_labeled=labeled_sample_df,
            X_unlabeled=unlabeled_sample_df,
            Y_labeled=label_df,
            label_encoder=label_encoder,
            START_SET_SIZE=3,
            hyper_parameters=self.config,
            oracle=ParallelOracle(
                sample_ids=sample_ids,
                pipe_endpoint=self.pipe_endpoint,
                label_encoder=label_encoder,
            ),
        )
