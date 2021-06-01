import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.metrics import accuracy_score
from .active_learning.al_cycle_wrapper import train_al
from .active_learning.experiment_setup_lib import init_logger
from .etikedi_oracle import EtikediOracle

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
    "RANDOM_SEED": 10,
    "N_JOBS": -1,
    "NR_LEARNING_ITERATIONS": 200000,
}

init_logger("log_example.txt")

iris = datasets.load_iris()

Y_true = iris["target"]

# fewer comments, but with better API
df = pd.DataFrame(
    data=np.c_[iris["data"], iris["target"]],
    columns=iris["feature_names"] + ["target"],
    dtype=float,
)
df.rename({"target": "label"}, axis="columns", inplace=True)

df.loc[~df.index.isin([0, 10, 60, 70, 100, 130]), "label"] = None

df.label.replace({0: "a", 1: "b", 2: "d"}, inplace=True)

print(df)

(_, _, metrics_per_al_cycle, data_storage, _) = train_al(
    hyper_parameters=config,
    oracle=EtikediOracle(),  # this class needs to be extended!
    df=df,
)

print(
    "Done with labeling {} new datapoints".format(
        sum(metrics_per_al_cycle["query_length"])
    )
)

print(data_storage.train_labeled_Y["label"].to_list())
print(Y_true)

# random sampling -> expected accuracy should be ~0.3333
print(accuracy_score(Y_true, data_storage.train_labeled_Y["label"].to_list()))
