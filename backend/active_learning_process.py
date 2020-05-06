import multiprocessing
import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from active_learning.BaseOracle import BaseOracle
from active_learning.al_cycle_wrapper import train_al
from active_learning.experiment_setup_lib import init_logger
from aergia import create_app
from models.flowers import Flower

class ParallelOracle(BaseOracle):

    def __init__(self, samples):
        self.samples = samples

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


app = create_app()
app.app_context().push()
config = {
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

init_logger("log.txt")
# Load Data from database
sepal_lengths = []
sepal_widths = []
petal_lengts = []
petal_widths = []
labels = []
flowers = Flower.query.all()
for flower in flowers:
    sepal_lengths.append(flower.sepal_length)
    sepal_widths.append(flower.sepal_width)
    petal_lengts.append(flower.petal_length)
    petal_widths.append(flower.petal_width)
    labels.append(flower.label)

#  dataset_id = Dataset.query.filter_by(name=self.dataset_name).first().id
# data = Sample.query.filter_by(dataset_id=dataset_id).all()
# unlabeled_data = Sample.query.filter_by(dataset_id=dataset_id, label != None).all()
#
# Depending on data set, convert data in suitable format

# X and Y need to be both of the same dataframe in order to have consistent indexing!
df = pd.DataFrame(
    data=np.c_[sepal_lengths, sepal_widths, petal_lengts, petal_widths, labels],
    columns=["sepal_length", "sepal_width", "petal_length", "petal_width", "label"],
    dtype=float,
)
X = df
Y = df.pop("target")
Y = pd.DataFrame(
    Y.to_numpy(), dtype=int
)  # important step: the column name of the Y dataframe has to be '0' as in now column, so call to_numpy() first to remove it
indices_of_start_set = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 50]

# the labeled dataset needs to contain at least one example of each class, so we include those in the labeled set, and everything else in the unlabeled  set, and forget as of now the labels for the unlabeled set
X_labeled = X.loc[indices_of_start_set]
Y_labeled = Y.loc[indices_of_start_set]
X_unlabeled = X.drop(indices_of_start_set)

# Get label meanings from data base
# label_encoder_classes = [label.name for label in Label.query.filter_by(dataset=dataset_id).all()]
label_encoder_classes = ["setosa", "versicolor", "virginica"]

label_encoder = LabelEncoder()
label_encoder.fit(label_encoder_classes)

print("Start Active-Learning")

# Y_train are the resulting labels
# metrics_per_al_cycle contains a lot of labels useful for visualisation
(_, Y_train, _, metrics_per_al_cycle, _, _) =  train_al(
    X_labeled,
    Y_labeled,
    X_unlabeled,
    label_encoder,
    START_SET_SIZE=3,
    hyper_parameters=config,
    oracle=ParallelOracle(),  # this class needs to be extended!
)


