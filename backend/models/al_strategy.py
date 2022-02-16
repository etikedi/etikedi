from __future__ import annotations  # necessary for self referencing annotations

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List, Type

from alipy.query_strategy.query_labels import QueryInstanceSPAL, QueryInstanceUncertainty, QueryInstanceLAL, \
    QueryInstanceBMDR, QueryInstanceRandom, QueryInstanceQUIRE, QueryInstanceQBC, \
    QueryExpectedErrorReduction, QueryInstanceGraphDensity
from fastapi.openapi.models import Schema
from pydantic import PositiveInt


class QKernel(str, Enum):
    linear = 'linear',
    poly = 'poly',
    rbf = 'rbf'


class QMeasureType(str, Enum):
    LEAST_CONFIDENT = "least_confident"
    MARGIN = "margin"
    ENTROPY = "entrop"
    DISTANCE_TO_BOUNDARY = "distance_to_boundar"


class QLALMode(str, Enum):
    LAL_ITERATIVE = "LAL_iterative"
    LAL_INDEPENDENT = "LAL_independent"


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


class QMethod(str, Enum):
    QUERY_BY_BAGGING = 'query_by_bagging'


class QDisagreement(str, Enum):
    VOTE_ENTROPY = "vote_entropy"
    KL_DIVERGENCE = "KL_divergence"


class QueryStrategyAbstraction(metaclass=ABCMeta):
    base_url = "http://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/huangsj/alipy/page_reference/api_classes/api_query_strategy.query_labels"

    @abstractmethod
    def select(self, label_index, unlabel_index, model, batch_size):
        pass

    @staticmethod
    def build(qs_type: QueryStrategyType, config, X, y):
        return qs_type.get_class()(X=X, y=y, config=config)

    @staticmethod
    @abstractmethod
    def get_config_schema() -> Type[Schema]:
        pass


class QueryInstanceSPALHolder(QueryStrategyAbstraction):
    class SPALConfig(Schema):
        description = QueryStrategyAbstraction.base_url + ".QueryInstanceSPAL.html"
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
        self.qp_solver = None
        self.qs = QueryInstanceSPAL(X=X,
                                    y=y,
                                    mu=config.mu,
                                    gamma=config.gamma,
                                    rho=config.rho,
                                    lambda_init=config.lambda_init,
                                    lambda_pace=config.lambda_pace)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size, self.qp_solver)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceSPALHolder.SPALConfig


class QueryInstanceUncertaintyHolder(QueryStrategyAbstraction):
    class UncertaintyConfig(Schema):
        description = QueryStrategyAbstraction.base_url + "QueryInstanceUncertainty.html"
        measure: QMeasureType = QMeasureType.LEAST_CONFIDENT

    def __init__(self, X, y, config: UncertaintyConfig):
        self.qs = QueryInstanceUncertainty(X=X,
                                           y=y,
                                           measure=config.measure.value)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceUncertaintyHolder.UncertaintyConfig


class QueryInstanceLALHolder(QueryStrategyAbstraction):
    class LALConfig(Schema):
        description = QueryStrategyAbstraction.base_url + "QueryInstanceLAL.html"
        mode: QLALMode = QLALMode.LAL_ITERATIVE
        data_path = "/data/alipy"
        cls_est: PositiveInt = 50
        train_slt: bool = True

    def __init__(self, X, y, config: LALConfig):
        self.qs = QueryInstanceLAL(X=X,
                                   y=y,
                                   **config.dict())

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceLALHolder.LALConfig


class QueryInstanceBMDRHolder(QueryStrategyAbstraction):
    class BMDRConfig(Schema):
        description = QueryStrategyAbstraction.base_url + "QueryInstanceBMDR.html"
        beta: float = 1000.0
        gamma: float = 0.1
        rho: float = 1.0
        kernel: QKernel = QKernel.rbf

    def __init__(self, X, y, config: BMDRConfig):
        self.qp_solver = None
        self.qs = QueryInstanceBMDR(X=X,
                                    y=y,
                                    beta=config.beta,
                                    gamma=config.gamma,
                                    rho=config.rho)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size, self.qp_solver)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceBMDRHolder.BMDRConfig


class QueryInstanceRandomHolder(QueryStrategyAbstraction):
    class RandomConfig(Schema):
        description = QueryStrategyAbstraction.base_url + "QueryInstanceRandom.html"

    def __init__(self, X, y, config: RandomConfig):
        self.qs = QueryInstanceRandom(X=X,
                                      y=y)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceRandomHolder.RandomConfig


class QueryInstanceGraphDensityHolder(QueryStrategyAbstraction):
    class GraphDensityConfig(Schema):
        description = QueryStrategyAbstraction.base_url + "QueryInstanceGraphDensity.html"
        train_idx: List = []  # injected by experiment
        metric: QMetric = QMetric.MANHATTAN

    def __init__(self, X, y, config: GraphDensityConfig):
        self.qs = QueryInstanceGraphDensity(X=X,
                                            y=y,
                                            train_idx=config.train_idx,
                                            metric=config.metric)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceGraphDensityHolder.GraphDensityConfig


class QueryInstanceQUIREHolder(QueryStrategyAbstraction):
    class QUIREConfig(Schema):
        description = QueryStrategyAbstraction.base_url + 'QueryInstanceQUIRE.html'
        train_idx: List = []  # injected by experiment
        lambda_arg: float = 1.0
        kernel: QKernel = QKernel.rbf
        degree: PositiveInt = 3  # only relevant for kernel = poly
        gamma: float = 1.0  # only relevant for kernel = rbf, poly
        coef: float = 1.0  # only relevant for kernel = poly

    def __init__(self, X, y, config: QUIREConfig):
        self.qs = QueryInstanceQUIRE(X=X,
                                     y=y,
                                     **config.dict())

    def select(self, label_index, unlabel_index, model, batch_size):
        results = []
        for _ in range(batch_size):
            results + self.qs.select(label_index, unlabel_index)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceQUIREHolder.QUIREConfig


class QueryInstanceQBCHolder(QueryStrategyAbstraction):
    class QBCConfig(Schema):
        description = QueryStrategyAbstraction.base_url + 'QueryInstanceQBC.html'
        method: QMethod = QMethod.QUERY_BY_BAGGING
        disagreement: QDisagreement

    def __init__(self, X, y, config: QBCConfig):
        self.n_jobs = None
        self.qs = QueryInstanceQBC(X=X,
                                   y=y,
                                   method=config.method,
                                   disagreement=config.disagreement.value)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size, self.n_jobs)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryInstanceQBCHolder.QBCConfig


class QueryExpectedErrorReductionHolder(QueryStrategyAbstraction):
    class ExpectedErrorReductionConfig(Schema):
        description = QueryStrategyAbstraction.base_url + "QueryExpectedErrorReduction.html"

    def __init__(self, X, y, config: ExpectedErrorReductionConfig):
        self.qs = QueryExpectedErrorReduction(X=X,
                                              y=y)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size)

    @staticmethod
    def get_config_schema() -> Type[Schema]:
        return QueryExpectedErrorReductionHolder.ExpectedErrorReductionConfig


class QueryStrategyType(str, Enum):
    QUERY_INSTANCE_BMDR = 'QueryInstanceBMDR',  # Requires pip cvxpy, only applicable for binary classification
    QUERY_INSTANCE_GRAPH_DENSITY = 'QueryInstanceGraphDensity',
    QUERY_INSTANCE_LAL = 'QueryInstanceLAL',  # Only applicable for binary classification
    QUERY_INSTANCE_QBC = 'QueryInstanceQBC',
    QUERY_INSTANCE_QUIRE = 'QueryInstanceQUIRE',
    QUERY_INSTANCE_SPAL = 'QueryInstanceSPAL',
    QUERY_INSTANCE_UNCERTAINTY = 'QueryInstanceUncertainty',
    QUERY_INSTANCE_RANDOM = 'QueryInstanceRandom',
    QUREY_EXPECTED_ERROR_REDUCTION = 'QueryExpectedErrorReduction'

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
        return self == QueryStrategyType.QUERY_INSTANCE_BMDR or \
               self == QueryStrategyType.QUERY_INSTANCE_LAL

    # returns all config options for this query strategy
    def get_config_schema(self) -> Type[Schema]:
        return self.get_class().get_config_schema()

    def get_default_config(self):
        ConfiClass = self.get_class().get_config_schema()
        return ConfiClass()  # instance of Schema
