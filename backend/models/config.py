from __future__ import annotations  # necessary for self referencing annotations
from enum import Enum
from typing import List, Optional, Union

from .al_strategy import QueryStrategyType

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from pydantic import (
    BaseModel as Schema,
    PositiveInt,
)


# all model that implement the scikit-learn api and provide predict_proba
class ALModel(str, Enum):
    DECISION_TREE_CLASSIFIER = "DecisionTreeClassifier"
    RANDOM_FOREST_CLASSIFIER = "RandomForestClassifier"
    LOGISTIC_REGRESSION = "LogisticRegression"

    def get_class(self):
        if self == ALModel.DECISION_TREE_CLASSIFIER:
            return DecisionTreeClassifier
        elif self == ALModel.RANDOM_FOREST_CLASSIFIER:
            return RandomForestClassifier
        elif self == ALModel.LOGISTIC_REGRESSION:
            return LogisticRegression


class StoppingCriteriaOption(str, Enum):
    ALL_LABELED = "all_labeled"
    NUM_OF_QUERIES = "num_of_queries"
    COST_LIMIT = "cost_limit"
    PERCENT_OF_UNLABEL = "percent_of_unlabel"
    CPU_TIME = "time_limit"

    # None has to be passed to StoppingCriteria() as absence of criteria which is equiv to all_labeled
    def get(self):
        return None if self == StoppingCriteriaOption.ALL_LABELED else self.value


class QMeasureType(str, Enum):
    LEAST_CONFIDENT = "least_confident"
    MARGIN = "margin"
    ENTROPY = "entrop"
    DISTANCE_TO_BOUNDARY = "distance_to_boundar"


class QLALMode(str, Enum):
    LAL_ITERATIVE = "LAL_iterative"
    LAL_INDEPENDENT = "LAL_independent"


class QQBCDisagreement(str, Enum):
    VOTE_ENTROPY = "vote_entropy"
    KL_DIVERGENCE = "KL_divergence"


class QMetric(str, Enum):
    EUCLIDEAN = ("euclidean",)
    L2 = "l2"
    L1 = "l1"
    MANHATTAN = "manhattan"
    CITYBLOCK = "cityblock"
    BRAYCURTIS = "braycurtis"
    CANBERRA = "canberra"
    CHEBYSHEV = "chebyshev"
    CORRELATION = "correlation"
    COSINE = "cosine"
    DICE = "dice"
    HAMMING = "hamming"
    JACCARD = "jaccard"
    KULSINSKI = "kulsinski"
    MAHALANOBIS = "mahalanobis"
    MATCHING = "matching"
    MINKOWSKI = "minkowski"
    ROGERSTANIMOTO = "rogerstanimoto"
    RUSSELLRAO = "russellrao"
    SEUCLIDEAN = "seuclidean"
    SOKALMICHENER = "sokalmichener"
    SOKALSNEATH = "sokalsneath"
    SQEUCLIDEAN = "sqeuclidean"
    YULE = "yule"
    WMINKOWSKI = "wminkowski"


class QueryStrategyConfig(Schema):
    beta = 1000  # QueryInstanceBMDR
    cls_est: PositiveInt = 50  # LAL
    data_path = "/data/alipy"  # LAL
    disagreement: QQBCDisagreement = QQBCDisagreement.VOTE_ENTROPY  # QueryInstanceQBC
    gamma = 0.1  # QueryInstanceSPAL, QueryInstanceBMDR
    lambda_init = 0.1  # QueryInstanceSPAL
    lambda_pace = 0.01  # QueryInstanceSPAL
    measure: QMeasureType = QMeasureType.LEAST_CONFIDENT
    method = "query_by_bagging"  # QueryInstanceQBC
    metric: QMetric = "manhattan"  # QueryInstanceGraphDensity
    mode: QLALMode = QLALMode.LAL_ITERATIVE  # LAL
    mu = 0.1  # QueryInstanceSPAL
    rho = 0.1  # QueryInstanceSPAL, QueryInstanceBMDR
    train_slt: bool = True  # LAL
    # injected by the experiment:
    train_idx: List = []  # QueryInstanceGraphDensity, QueryInstanceQUIRE


class ActiveLearningConfig(Schema):
    QUERY_STRATEGY: QueryStrategyType = QueryStrategyType.QUERY_INSTANCE_RANDOM
    QUERY_STRATEGY_CONFIG: QueryStrategyConfig = QueryStrategyConfig()
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER
    STOPPING_CRITERIA: StoppingCriteriaOption = StoppingCriteriaOption.ALL_LABELED
    STOPPING_CRITERIA_VALUE: Optional[Union[int, float]]
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request
    COUNTER_UNTIL_NEXT_EVAL: PositiveInt = (
        5  # number of updates (add/remove) until next model evaluation
    )
    EVALUATION_SIZE: PositiveInt = 5  # number of updates until next model training
    COUNTER_UNTIL_NEXT_MODEL_UPDATE: PositiveInt = 5
    # Etikedi config options
    RANDOM_SAMPLE_EVERY: PositiveInt = 10
    TIMEOUT_FOR_WORKER: PositiveInt = 60

    DATASET_NAME: str = "Dataset"
    AMOUNT_OF_FEATURES: int = -1


default_al_config = ActiveLearningConfig()
