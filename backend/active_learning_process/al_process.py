import multiprocessing
from io import StringIO

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from ..active_learning.al_cycle_wrapper import train_al
from ..active_learning.experiment_setup_lib import init_logger
from ..config import app, db
from ..models import Association, Sample, Dataset
from .al_oracle import ParallelOracle
from .db_functions import samples_of_dataset, samples_to_feature_dict, query_flowers, check_for_label, \
    labels_of_dataset, dataset_name_by_dataset_id


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

    def run(self):
        """
        This methods represents the entry point to the active-learning code.
        Before it can be started, data has to get retrieved from database.
        This is done via a member of this class which allows an unambiguously identification of the queried dataset.
        After the data preparation is done, a BaseOracle object is created and - including with the configuration and
        data -  fed to the active learning code.
        """
        init_logger("log.txt")
        sample_ids = {}
        features, labels, indices_labeled_data, label_meanings = [], [], [], []
        dataset_name = dataset_name_by_dataset_id(self.dataset_id)
        dataset = Dataset.query.get(self.dataset_id)
        app.logger.info("ALProcess:\tStarting for dataset {}".format(self.dataset_id))
        
        # Data preparation for usage of aL-code with iris-dataset (test)
        # if dataset_name == "":
        #     samples = query_flowers()
        #     for i in range(len(samples)):
        #         sample = samples[i]
        #         sample_ids[i] = sample.id
        #         features.append([sample.sepal_length, sample.sepal_width, sample.petal_length, sample.petal_width])
        #         labels.append(sample.label)
        #         indices_labeled_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 50]
        #     feature_array = np.array(features, dtype='float')
        #     feature_names = ["sepal length", "sepal width", "petal length", "petal width"]
        #     label_meanings = ["setosa", "versicolor", "virginica"]

        buffer = StringIO(dataset.features)
        sample_df = pd.read_csv(buffer).set_index('ID')  # = X, in the example

        # important step: the column name of the Y dataframe has to be '0' as in now column, so call to_numpy()
        # first to remove it

        associated_labels = db.session.query(
            Association.sample_id, Association.label_id
        ).join(Association.sample).filter(Sample.dataset == dataset).all()

        label_df = pd.DataFrame(associated_labels, columns=['ID', 0]).set_index('ID')
        ids_of_labeled_samples = np.array(associated_labels)[:,0]

        # label_df = pd.DataFrame(label_df.to_numpy(), dtype=int).loc[indices_labeled_data]

        # X => features
        # Y => pandas.Series containing only the labels

        # the labeled dataset needs to contain at least one example of each class, so we include those in the labeled
        # set, and everything else in the unlabeled  set, and forget as of now the labels for the unlabeled set
        labeled_sample_df = sample_df.loc[ids_of_labeled_samples]
        unlabeled_sample_df = sample_df.drop(ids_of_labeled_samples)

        # Get label meanings from data base
        label_encoder_classes = label_meanings
        label_encoder = LabelEncoder()
        label_encoder.fit(label_encoder_classes)

        # Y_train are the resulting labels
        # metrics_per_al_cycle contains a lot of labels useful for visualisation
        (_, Y_train, _, metrics_per_al_cycle, _, _) = train_al(
            X_labeled=labeled_sample_df,
            X_unlabeled=unlabeled_sample_df,
            Y_labeled=label_df,
            label_encoder=label_encoder,
            START_SET_SIZE=3,
            hyper_parameters=self.config,
            oracle=ParallelOracle(sample_ids, self.pipe_endpoint)
        )

        print('Done with the AL code')
