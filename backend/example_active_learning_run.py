import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import LabelEncoder

from backend.active_learning.al_cycle_wrapper import train_al
from backend.active_learning.experiment_setup_lib import (
    init_logger,
)
from backend.aergia_oracle import AergiaOracle

if __name__ == "__main__":
    config = {
        "SAMPLING": "uncertainty_max_margin",
        "CLUSTER": "MostUncertain_max_margin",
        "NR_QUERIES_PER_ITERATION": 100,
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

    iris = datasets.load_iris()

    # X and Y need to be both of the same dataframe in order to have consistent indexing!
    df = pd.DataFrame(
        data=np.c_[iris["data"], iris["target"]],
        columns=iris["feature_names"] + ["target"],
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

    label_encoder_classes = ["setosa", "versicolor", "virginica"]

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
        hyper_parameters=config,
        oracle=AergiaOracle(),  # this class needs to be extended!
    )

    print(
        "Done with labeling {} new datapoints".format(
            sum(metrics_per_al_cycle["query_length"])
        )
    )
