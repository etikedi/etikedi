from __future__ import annotations  # necessary for self referencing annotations

from abc import ABCMeta, abstractmethod
from copy import deepcopy
from enum import Enum
from typing import List, Type, Literal, Dict

import numpy as np
from alipy.query_strategy.query_labels import (
    QueryInstanceSPAL,
    QueryInstanceUncertainty,
    QueryInstanceLAL,
    QueryInstanceBMDR,
    QueryInstanceRandom,
    QueryInstanceQUIRE,
    QueryInstanceQBC,
    QueryExpectedErrorReduction,
    QueryInstanceGraphDensity,
)
from fastapi.openapi.models import BaseModel
from pydantic import PositiveInt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


class QKernel(str, Enum):
    linear = "linear"
    poly = "poly"
    rbf = "rbf"


class QMeasureType(str, Enum):
    LEAST_CONFIDENT = "least_confident"
    MARGIN = "margin"
    ENTROPY = "entropy"
    # only for binary classification requires the model to have 'decision_function'
    DISTANCE_TO_BOUNDARY = "distance_to_boundary"


class QLALMode(str, Enum):
    LAL_ITERATIVE = "LAL_iterative"
    LAL_INDEPENDENT = "LAL_independent"

class QpSolver(str, Enum):
    ECOS = 'ECOS',
    OSQP = 'OSQP'

class QMetric(str, Enum):
    EUCLIDEAN = "euclidean"
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


class QMethod(str, Enum):
    QUERY_BY_BAGGING = "query_by_bagging"


class QDisagreement(str, Enum):
    VOTE_ENTROPY = "vote_entropy"
    KL_DIVERGENCE = "KL_divergence"


# all model that implement the scikit-learn api and provide predict_proba
class ALModel(str, Enum):
    DECISION_TREE_CLASSIFIER = "DecisionTreeClassifier"
    RANDOM_FOREST_CLASSIFIER = "RandomForestClassifier"
    LOGISTIC_REGRESSION = "LogisticRegression"
    NAIVE_BAYES = "NaiveBayes"
    SVC = "SVC"
    MLP = "MLPClassifier"

    def get_class(self):
        if self == ALModel.DECISION_TREE_CLASSIFIER:
            return DecisionTreeClassifier
        elif self == ALModel.RANDOM_FOREST_CLASSIFIER:
            return RandomForestClassifier
        elif self == ALModel.LOGISTIC_REGRESSION:
            return LogisticRegression
        elif self == ALModel.NAIVE_BAYES:
            return GaussianNB
        elif self == ALModel.SVC:
            return SVC
        elif self == ALModel.MLP:
            return MLPClassifier


class StoppingCriteriaOption(str, Enum):
    ALL_LABELED = "all_labeled"
    NUM_OF_QUERIES = "num_of_queries"
    COST_LIMIT = "cost_limit"
    PERCENT_OF_UNLABEL = "percent_of_unlabel"
    CPU_TIME = "time_limit"

    # None has to be passed to StoppingCriteria() as absence of criteria which is equiv to all_labeled
    def get(self):
        return None if self == StoppingCriteriaOption.ALL_LABELED else self.value


class QueryStrategyAbstraction(metaclass=ABCMeta):
    base_url = (
        "https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/huangsj/alipy/page_reference"
        "/api_classes/api_query_strategy.query_labels "
    )

    @abstractmethod
    def select(self, label_index, unlabel_index, model, batch_size):
        pass

    @staticmethod
    def build(qs_type: QueryStrategyType, config, X, y):
        return qs_type.get_class()(X=X, y=y, config=config)

    @staticmethod
    @abstractmethod
    def get_config_model() -> Type[BaseModel]:
        pass

    @staticmethod
    @abstractmethod
    def get_config_schema(binary: bool = False) -> Dict:
        pass


class QueryInstanceSPALHolder(QueryStrategyAbstraction):
    class SPALConfig(BaseModel):
        query_type: Literal["QueryInstanceSPAL"]
        description = QueryStrategyAbstraction.base_url + ".QueryInstanceSPAL.html"
        qp_solver: QpSolver = QpSolver.ECOS
        mu: float = 0.1
        gamma: float = 0.1
        rho: float = 1.0
        lambda_init: float = 0.1
        lambda_pace: float = 0.01
        kernel: QKernel = QKernel.rbf
        degree: PositiveInt = 3
        gamma_ker: float = 1.0  # only for kernel = rbf or poly
        coef0: float = 1.0  # only for kernel = poly

    def __init__(self, X, y, config: SPALConfig):
        self.qp_solver = config.qp_solver
        self.qs = QueryInstanceSPAL(
            X=X,
            y=workaround_integer_label_binary_classification(y),
            mu=config.mu,
            gamma=config.gamma,
            rho=config.rho,
            lambda_init=config.lambda_init,
            lambda_pace=config.lambda_pace,
        )

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size, self.qp_solver)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceSPALHolder.SPALConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceSPALHolder.get_config_model().schema()


class QueryInstanceUncertaintyHolder(QueryStrategyAbstraction):
    class UncertaintyConfig(BaseModel):
        query_type: Literal["QueryInstanceUncertainty"]
        description = (
                QueryStrategyAbstraction.base_url + "QueryInstanceUncertainty.html"
        )
        # validation done in additional_experiment_validation (distance_to_boundary only for binary label)
        measure: QMeasureType = QMeasureType.LEAST_CONFIDENT

    def __init__(self, X, y, config: UncertaintyConfig):
        self.qs = QueryInstanceUncertainty(X=X, y=y, measure=config.measure.value)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceUncertaintyHolder.UncertaintyConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        if binary:
            return QueryInstanceUncertaintyHolder.get_config_model().schema()
        else:
            # validation done in additional_experiment_validation
            schema = deepcopy(QueryInstanceUncertaintyHolder.get_config_model().schema())
            schema['definitions']['QMeasureType']['enum'].remove('distance_to_boundary')
            return schema


class QueryInstanceLALHolder(QueryStrategyAbstraction):
    class LALConfig(BaseModel):
        query_type: Literal["QueryInstanceLAL"]
        description = QueryStrategyAbstraction.base_url + "QueryInstanceLAL.html"
        mode: QLALMode = QLALMode.LAL_ITERATIVE
        data_path = "/data/alipy"
        cls_est: PositiveInt = 50
        train_slt: bool = True

    def __init__(self, X, y, config: LALConfig):
        self.qs = QueryInstanceLAL(X=X, y=y, **config.dict())

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceLALHolder.LALConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceLALHolder.get_config_model().schema()


class QueryInstanceBMDRHolder(QueryStrategyAbstraction):
    class BMDRConfig(BaseModel):
        query_type: Literal["QueryInstanceBMDR"]
        qp_solver: QpSolver = QpSolver.ECOS
        description = QueryStrategyAbstraction.base_url + "QueryInstanceBMDR.html"
        beta: float = 1000.0
        gamma: float = 0.1
        rho: float = 1.0
        kernel: QKernel = QKernel.rbf

    def __init__(self, X, y, config: BMDRConfig):
        self.qp_solver = config.qp_solver
        self.qs = QueryInstanceBMDR(
            X=X,
            y=workaround_integer_label_binary_classification(y),
            beta=config.beta,
            gamma=config.gamma,
            rho=config.rho
        )

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size, self.qp_solver)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceBMDRHolder.BMDRConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceBMDRHolder.get_config_model().schema()


class QueryInstanceRandomHolder(QueryStrategyAbstraction):
    class RandomConfig(BaseModel):
        query_type: Literal["QueryInstanceRandom"]
        description = QueryStrategyAbstraction.base_url + "QueryInstanceRandom.html"

    def __init__(self, X, y, config: RandomConfig):
        self.qs = QueryInstanceRandom(X=X, y=y)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceRandomHolder.RandomConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceRandomHolder.get_config_model().schema()


class QueryInstanceGraphDensityHolder(QueryStrategyAbstraction):
    class GraphDensityConfig(BaseModel):
        query_type: Literal["QueryInstanceGraphDensity"]
        description = (
                QueryStrategyAbstraction.base_url + "QueryInstanceGraphDensity.html"
        )
        train_idx: List = []  # injected by experiment
        metric: QMetric = QMetric.MANHATTAN

    def __init__(self, X, y, config: GraphDensityConfig):
        self.qs = QueryInstanceGraphDensity(
            X=X, y=y, train_idx=config.train_idx, metric=config.metric
        )

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceGraphDensityHolder.GraphDensityConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceGraphDensityHolder.get_config_model().schema()


class QueryInstanceQUIREHolder(QueryStrategyAbstraction):
    class QUIREConfig(BaseModel):
        query_type: Literal["QueryInstanceQUIRE"]
        description = QueryStrategyAbstraction.base_url + "QueryInstanceQUIRE.html"
        train_idx: List = []  # injected by experiment
        lambda_arg: float = 1.0
        kernel: QKernel = QKernel.rbf
        degree: PositiveInt = 3  # only relevant for kernel = poly
        gamma: float = 1.0  # only relevant for kernel = rbf, poly
        coef: float = 1.0  # only relevant for kernel = poly

    def __init__(self, X, y, config: QUIREConfig):
        self.qs = QueryInstanceQUIRE(X=X, y=y, **config.dict())

    def select(self, label_index, unlabel_index, model, batch_size):
        results = []
        for _ in range(batch_size):
            results + self.qs.select(label_index, unlabel_index)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceQUIREHolder.QUIREConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceQUIREHolder.get_config_model().schema()


class QueryInstanceQBCHolder(QueryStrategyAbstraction):
    class QBCConfig(BaseModel):
        query_type: Literal["QueryInstanceQBC"]
        description = QueryStrategyAbstraction.base_url + "QueryInstanceQBC.html"
        method: QMethod = QMethod.QUERY_BY_BAGGING
        disagreement: QDisagreement = QDisagreement.VOTE_ENTROPY

    def __init__(self, X, y, config: QBCConfig):
        self.n_jobs = None
        self.qs = QueryInstanceQBC(
            X=X, y=y, method=config.method, disagreement=config.disagreement.value
        )

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(
            label_index, unlabel_index, model, batch_size, self.n_jobs
        )

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryInstanceQBCHolder.QBCConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryInstanceQBCHolder.get_config_model().schema()


class QueryExpectedErrorReductionHolder(QueryStrategyAbstraction):
    class ExpectedErrorReductionConfig(BaseModel):
        query_type: Literal["QueryExpectedErrorReduction"]
        description = (
                QueryStrategyAbstraction.base_url + "QueryExpectedErrorReduction.html"
        )

    def __init__(self, X, y, config: ExpectedErrorReductionConfig):
        self.qs = QueryExpectedErrorReduction(X=X, y=y)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size)

    @staticmethod
    def get_config_model() -> Type[BaseModel]:
        return QueryExpectedErrorReductionHolder.ExpectedErrorReductionConfig

    @staticmethod
    def get_config_schema(binary: bool = False) -> Dict:
        return QueryExpectedErrorReductionHolder.get_config_model().schema()


class QueryStrategyType(str, Enum):
    QUERY_INSTANCE_BMDR = (
        "QueryInstanceBMDR",
    )  # Requires pip cvxpy, only applicable for binary classification
    QUERY_INSTANCE_GRAPH_DENSITY = ("QueryInstanceGraphDensity",)
    QUERY_INSTANCE_LAL = (
        "QueryInstanceLAL",
    )  # Only applicable for binary classification
    QUERY_INSTANCE_QBC = ("QueryInstanceQBC",)
    QUERY_INSTANCE_QUIRE = ("QueryInstanceQUIRE",)
    QUERY_INSTANCE_SPAL = ("QueryInstanceSPAL",)
    QUERY_INSTANCE_UNCERTAINTY = ("QueryInstanceUncertainty",)
    QUERY_INSTANCE_RANDOM = ("QueryInstanceRandom",)
    QUREY_EXPECTED_ERROR_REDUCTION = "QueryExpectedErrorReduction"

    def get_class(self):
        if self == QueryStrategyType.QUERY_INSTANCE_BMDR:
            return QueryInstanceBMDRHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_GRAPH_DENSITY:
            return QueryInstanceGraphDensityHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_LAL:
            return QueryInstanceLALHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_QBC:
            return QueryInstanceQBCHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_QUIRE:
            return QueryInstanceQUIREHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_SPAL:
            return QueryInstanceSPALHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_UNCERTAINTY:
            return QueryInstanceUncertaintyHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_RANDOM:
            return QueryInstanceRandomHolder
        elif self == QueryStrategyType.QUREY_EXPECTED_ERROR_REDUCTION:
            return QueryExpectedErrorReductionHolder

    def only_binary_classification(self):
        return (
                self == QueryStrategyType.QUERY_INSTANCE_BMDR
                or self == QueryStrategyType.QUERY_INSTANCE_LAL
                or self == QueryStrategyType.QUERY_INSTANCE_SPAL
        )

    # returns all config options for this query strategy
    def get_config_model(self) -> Type[BaseModel]:
        return self.get_class().get_config_model()

    def get_config_schema(self, binary: bool = False):
        return self.get_class().get_config_schema(binary)

    def get_default_config(self):
        ConfigClass = self.get_class().get_config_model()
        return ConfigClass(query_type=self.value)  # instance of Schema


def workaround_integer_label_binary_classification(y: np.ndarray) -> np.ndarray:
    # TODO
    # workaround for possible bug in alipy
    # TypeError: ufunc 'add' output (typecode 'O') could not be coerced
    # alipy fails in query_labels line 1573: delta += self._rho * (z - theta.dot(vKlu)
    # because when transforming y to [-1 | 1] self.y is not of dtype int | float
    ul = np.unique(y)
    if len(ul) == 2 and {1, -1} != set(ul):
        y_number = np.array(list(map(lambda x: 1 if x == ul[0] else -1, y)))
        return y_number
    return y