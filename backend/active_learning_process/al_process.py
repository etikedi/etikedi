import multiprocessing
import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from active_learning.BaseOracle import BaseOracle
from active_learning.al_cycle_wrapper import train_al
from active_learning.experiment_setup_lib import init_logger
from active_learning_process import al_config
from active_learning_process.db_functions import samples_of_dataset, samples_to_feature_dict, \
    add_to_label_queue, query_new_labels, delete_from_label_queue, query_flowers
from active_learning_process.feature_resolving import FeatureResolver


class ALProcess(multiprocessing.Process):

    def __init__(self, dataset_name):
        super().__init__()
        self.dataset_name = dataset_name
        self.config = al_config.config()

    def run(self):
        init_logger("log.txt")
        sample_ids = {}
        features = []
        labels = []
        indices_labeled_data = []
        label_meanings = []
        print("Active learning process started for dataset: " + self.dataset_name)

        # Data preparation for usage of aL-code with iris-dataset (test)
        if self.dataset_name == "iris":
            samples = query_flowers()
            for i in range(len(samples)):
                sample = samples[i]
                sample_ids[i] = sample.id
                features.append([sample.sepal_length, sample.sepal_width, sample.petal_length, sample.petal_width])
                labels.append(sample.label)
                indices_labeled_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 50]
            feature_array = np.array(features, dtype='float')
            feature_names = ["sepal length", "sepal width", "petal length", "petal width"]
            label_meanings = ["setosa", "versicolor", "virginica"]

        # Data preparation for usage of aL-code with proper data
        else:
            samples = samples_of_dataset(self.dataset_name)
            features = samples_to_feature_dict(samples)
            for i in range(len(samples)):
                sample = samples[i]
                sample_ids[i] = sample.id
                labels.append(sample.label.id)
                if sample.label is not None:
                    indices_labeled_data.append(i)

            # TODO Features-Resolving
            (feature_array, feature_names) = FeatureResolver(self.dataset_name, features, sample_ids).resolve()

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

        # the labeled dataset needs to contain at least one example of each class, so we include those in the labeled set, and everything else in the unlabeled  set, and forget as of now the labels for the unlabeled set
        X_labeled = X.loc[indices_labeled_data]
        Y_labeled = Y.loc[indices_labeled_data]
        X_unlabeled = X.drop(indices_labeled_data)

        # Get label meanings from data base
        label_encoder_classes = label_meanings
        label_encoder = LabelEncoder()
        label_encoder.fit(label_encoder_classes)

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


class ParallelOracle(BaseOracle):

    def __init__(self, sample_ids):
        self.sample_ids = sample_ids

    def get_labels(self, query_indices, data_storage):
        query_sample_ids = tuple([self.sample_ids[index] for index in tuple(query_indices)])
        print("Requesting labels for samples with ids " + str(query_sample_ids))
        add_to_label_queue(query_sample_ids)
        labels = []
        while len(query_indices) is not len(labels):
            print("Checking for requested labels")
            for sample_id in query_sample_ids:
                association = query_new_labels(sample_id)
                if association is not None:
                    label = association.label_id
                    labels.append(label)
                else:
                    print("\tRequested labels incomplete")
                    time.sleep(5)
                    break
        print("Requested labels complete. Current iteration successfully terminated")
        delete_from_label_queue(query_sample_ids)
        return labels
