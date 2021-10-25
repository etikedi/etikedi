from enum import Enum
from abc import ABCMeta, abstractmethod
from alipy.query_strategy.query_labels import QueryInstanceSPAL, QueryInstanceUncertainty, QueryInstanceLAL, \
    QueryInstanceBMDR, QueryInstanceRandom, QueryInstanceQUIRE, QueryInstanceQBC, \
    QueryExpectedErrorReduction, QueryInstanceGraphDensity
from typing import ForwardRef

QueryStrategyType = ForwardRef('QueryStrategyType')


class QueryStrategyAbstraction(metaclass=ABCMeta):

    @abstractmethod
    def select(self, label_index, unlabel_index, model, batch_size):
        pass

    @staticmethod
    def build(qs_type: QueryStrategyType, config, X, y):
        return qs_type.get_class()(X=X,y=y, config=config)


class QueryInstanceSPALHolder(QueryStrategyAbstraction):

    def __init__(self, X, y, config):
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


class QueryInstanceUncertaintyHolder(QueryStrategyAbstraction):

    def __init__(self, X, y, config):
        self.qs = QueryInstanceUncertainty(X=X,
                                           y=y,
                                           measure=config.measure.value)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size)


class QueryInstanceLALHolder(QueryStrategyAbstraction):

    def __init__(self, X, y, config):
        self.qs = QueryInstanceLAL(X=X,
                                   y=y,
                                   mode=config.mode.value,
                                   data_path=config.data_path,
                                   cls_est=config.cls_est,
                                   train_slt=config.train_slt)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)


class QueryInstanceBMDRHolder(QueryStrategyAbstraction):
    def __init__(self, X, y, config):
        self.qp_solver = None
        self.qs = QueryInstanceBMDR(X=X,
                                    y=y,
                                    beta=config.beta,
                                    gamma=config.gamma,
                                    rho=config.rho)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size, self.qp_solver)


class QueryInstanceRandomHolder(QueryStrategyAbstraction):
    def __init__(self, X, y, config):
        self.qs = QueryInstanceRandom(X=X,
                                      y=y)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)


class QueryInstanceGraphDensityHolder(QueryStrategyAbstraction):
    def __init__(self, X, y, config):
        self.qs = QueryInstanceGraphDensity(X=X,
                                            y=y,
                                            train_idx=config.train_idx,
                                            metric=config.metric)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, batch_size)


class QueryInstanceQUIREHolder(QueryStrategyAbstraction):
    def __init__(self, X, y, config):
        self.qs = QueryInstanceQUIRE(X=X,
                                     y=y,
                                     train_idx=config.train_idx)

    def select(self, label_index, unlabel_index, model, batch_size):
        results = []
        for _ in range(batch_size):
            results + self.qs.select(label_index, unlabel_index)


class QueryInstanceQBCHolder(QueryStrategyAbstraction):
    def __init__(self, X, y, config):
        self.n_jobs = None
        self.qs = QueryInstanceQBC(X=X,
                                   y=y,
                                   method=config.method,
                                   disagreement=config.disagreement.value)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size, self.n_jobs)


class QueryExpectedErrorReductionHolder(QueryStrategyAbstraction):
    def __init__(self, X, y, config):
        self.qs = QueryExpectedErrorReduction(X=X,
                                              y=y)

    def select(self, label_index, unlabel_index, model, batch_size):
        return self.qs.select(label_index, unlabel_index, model, batch_size)


class QueryStrategyType(str, Enum):
    QUERY_INSTANCE_BMDR = 'QueryInstanceBMDR',
    QUERY_INSTANCE_GRAPH_DENSITY = 'QueryInstanceGraphDensity',
    QUERY_INSTANCE_LAL = 'QueryInstanceLAL',
    QUERY_INSTANCE_QBC = 'QueryInstanceQBC',
    QUERY_INSTANCE_QUIRE = 'QueryInstanceQUIRE',
    QUERY_INSTANCE_SPAL = 'QueryInstanceSPAL',
    QUERY_INSTANCE_UNCERTAINTY = 'QueryInstanceUncertainty',
    QUERY_INSTANCE_RANDOM = 'QueryInstanceRandom',
    QUREY_EXPECTED_ERROR_REDUCTION = 'QueryExpectedErrorReduction'

    def get_class(self):
        if self == QueryStrategyType.QUERY_INSTANCE_BMDR:
            return QueryInstanceBMDRHolder
        elif self == QueryStrategyType.QUERY_INSTANCE_BMDR:
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
