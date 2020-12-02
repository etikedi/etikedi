import numpy as np
import pandas as pd
from pandas import DataFrame, Int64Index
from sklearn import datasets
from sklearn.metrics import accuracy_score

from ..active_learning.al_cycle_wrapper import train_al
from ..config import db
from ..example.aergia_oracle import AergiaOracle
from ..models import Dataset, Sample
from ..worker import manager, prepare_dataset_for_active_learning


cifar: Dataset = db.query(Dataset).filter_by(name='CIFAR').first()
sample_config = {
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


def test_active_learning_cifar():
    """ The active learning code should be able to get a CIFAR sample in 120 seconds """
    timeout = 3 * 60
    process_resources = manager.get_or_else_load(dataset=cifar)

    print('Start polling')
    has_new_samples = process_resources.pipe.poll(timeout)
    print(has_new_samples)

    sample_id = process_resources.pipe.recv()
    assert isinstance(sample_id, int)

    sample = db.query(Sample).filter_by(id=sample_id).first()
    assert sample
    assert sample.dataset_id == cifar.id


def get_iris_for_active_learning() -> DataFrame:
    iris = datasets.load_iris()

    df = pd.DataFrame(
        data=np.c_[iris["data"], iris["target"]],
        columns=iris["feature_names"] + ["target"],
        dtype=float,
    )
    df.rename({"target": "label"}, axis="columns", inplace=True)
    df.loc[~df.index.isin([0, 10, 60, 70, 100, 130]), "label"] = None
    df.label.replace({0: "a", 1: "b", 2: "d"}, inplace=True)

    return df


# def test_active_learning_iris():
#     iris = get_iris_for_active_learning()
#
#     (_, _, metrics_per_al_cycle, data_storage, _) = train_al(
#         hyper_parameters=sample_config,
#         oracle=AergiaOracle(),  # this class needs to be extended!
#         df=iris,
#     )
#
#     score = accuracy_score(
#         y_true=iris["label"],
#         y_pred=data_storage.train_labeled_Y["label"].to_list()
#     )
#
#     # Score should be around ~0.3333
#     assert abs(score - 0.3333) < 0.5


def test_prepare_cifar():
    cifar = db.query(Dataset).filter_by(name='CIFAR').first()
    df = prepare_dataset_for_active_learning(cifar)
    assert isinstance(df.index, Int64Index)
    assert 'label' in df.columns
    assert len(df.columns) >= 2


def test_prepare_dwtc():
    dwtc = db.query(Dataset).filter_by(name='DWTC').first()
    df = prepare_dataset_for_active_learning(dwtc)
    assert isinstance(df.index, Int64Index)
    assert 'label' in df.columns
    assert len(df.columns) >= 2
