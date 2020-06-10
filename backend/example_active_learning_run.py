import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import LabelEncoder

from .active_learning.al_cycle_wrapper import train_al
from .active_learning.experiment_setup_lib import init_logger
from .aergia_oracle import AergiaOracle

from .config import active_learning_config as config


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
    hyper_parameters=config.__dict__,
    oracle=AergiaOracle(),  # this class needs to be extended!
)

print(
    "Done with labeling {} new datapoints".format(
        sum(metrics_per_al_cycle["query_length"])
    )
)
