import multiprocessing
import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from backend.active_learning.al_cycle_wrapper import train_al
from backend.active_learning.experiment_setup_lib import init_logger
from backend.active_learning_process.aergia_oracle import ParallelOracle
from backend.active_learning_process.feature_resolving import FeatureResolver
from backend.models import Dataset, Sample, Label


class ALProcess(multiprocessing.Process):

    def __init__(self, dataset_name):
        super().__init__()
        self.dataset_name = dataset_name
        self.config = {
            "SAMPLING": "uncertainty_max_margin",
            "CLUSTER": "MostUncertain_max_margin",
            "NR_QUERIES_PER_ITERATION": 10,
            "WITH_UNCERTAINTY_RECOMMENDATION": True,
            "WITH_CLUSTER_RECOMMENDATION": True,
            "WITH_SNUBA_LITE": False,
            "MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS": 0,
            "UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD": 0.99,
            "UNCERTAINTY_RECOMMENDATION_RATIO": 0.01,
            "CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED": 0.8,
            "CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE": 0.3,
            "ALLOW_RECOMMENDATIONS_AFTER_STOP": True,
            "STOPPING_CRITERIA_UNCERTAINTY": 0,
            "STOPPING_CRITERIA_ACC": 0,
            "STOPPING_CRITERIA_STD": 0,
            "USER_QUERY_BUDGET_LIMIT": 2000,
            "RANDOM_SEED": -1,
            "N_JOBS": -1,
            "NR_LEARNING_ITERATIONS": 200000,
        }

    def run(self):

        init_logger("log.txt")

        # Load Data from database
        dataset_id = Dataset.query.filter_by(name=self.dataset_name).first().id
        label_names = [label.name for label in Label.query.filter_by(dataset_id=dataset_id).all()]
        data = Sample.query.filter_by(dataset_id=dataset_id).all()

        sample_ids = []
        features = []
        labels = []
        indices_labeled_data = []

        for i in range(len(data)):
            data_point = data[i]
            sample_ids.append(data_point.id)
            features.append(data_point.features)
            labels.append(data_point.label)
            if data_point.label is not None:
                indices_labeled_data.append(i)

        # TODO Features-Resolving
        (feature_array, feature_names) = FeatureResolver(dataset_id, features).resolve()

        # X and Y need to be both of the same dataframe in order to have consistent indexing!
        df = pd.DataFrame(
            data=np.c_[feature_array, labels],
            columns=feature_names + ["target"],
            dtype=float,
        )
        X = df
        Y = df.pop("target")
        Y = pd.DataFrame(
            Y.to_numpy(), dtype=int
        )  # important step: the column name of the Y dataframe has to be '0' as in now column, so call to_numpy() first to remove it
        indices_of_start_set = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 50]

        # the labeled dataset needs to contain at least one example of each class, so we include those in the labeled set, and everything else in the unlabeled  set, and forget as of now the labels for the unlabeled set
        X_labeled = X.loc[indices_labeled_data]
        Y_labeled = Y.loc[indices_labeled_data]
        X_unlabeled = X.drop(indices_labeled_data)

        # Get label meanings from data base
        # label_encoder_classes = [label.name for label in Label.query.filter_by(dataset=dataset_id).all()]
        label_encoder_classes = label_names

        label_encoder = LabelEncoder()
        label_encoder.fit(label_encoder_classes)

        print("Start Active-Learning")

        # Y_train are the resulting labels
        # metrics_per_al_cycle contains a lot of labels useful for visualisation
        (_, Y_train, _, metrics_per_al_cycle, _, _) = train_al(
            X_labeled,
            Y_labeled,
            X_unlabeled,
            label_encoder,
            START_SET_SIZE=3,
            hyper_parameters=self.config,
            oracle=ParallelOracle(sample_ids),  # this class needs to be extended!
        )
