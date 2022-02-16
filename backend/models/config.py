from __future__ import annotations  # necessary for self referencing annotations

from enum import Enum
from typing import Optional, Union

from pydantic import (
    BaseModel as Schema,
    PositiveInt, validator, )
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from .al_strategy import (
    QueryStrategyType,
    QueryInstanceBMDRHolder,
    QueryInstanceGraphDensityHolder,
    QueryInstanceLALHolder,
    QueryInstanceQBCHolder,
    QueryInstanceQUIREHolder,
    QueryInstanceSPALHolder,
    QueryInstanceUncertaintyHolder,
    QueryInstanceRandomHolder,
    QueryExpectedErrorReductionHolder,
)
from .battle import AlExperimentConfig


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


class ActiveLearningConfig(Schema):
    QUERY_STRATEGY: QueryStrategyType = QueryStrategyType.QUERY_INSTANCE_RANDOM
    QUERY_STRATEGY_CONFIG: Union[
        QueryInstanceBMDRHolder.BMDRConfig,
        QueryInstanceGraphDensityHolder.GraphDensityConfig,
        QueryInstanceLALHolder.LALConfig,
        QueryInstanceQBCHolder.QBCConfig,
        QueryInstanceQUIREHolder.QUIREConfig,
        QueryInstanceSPALHolder.SPALConfig,
        QueryInstanceUncertaintyHolder.UncertaintyConfig,
        QueryInstanceRandomHolder.RandomConfig,
        QueryExpectedErrorReductionHolder.ExpectedErrorReductionConfig,
    ] = QUERY_STRATEGY.get_default_config()
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER
    STOPPING_CRITERIA: StoppingCriteriaOption = StoppingCriteriaOption.ALL_LABELED
    STOPPING_CRITERIA_VALUE: Optional[Union[int, float]]
    # number of samples suggested per request
    BATCH_SIZE: PositiveInt = 5
    # number of updates (add/remove) until next model evaluation
    COUNTER_UNTIL_NEXT_EVAL: PositiveInt = 5
    # number of updates until next model training
    EVALUATION_SIZE: PositiveInt = 5
    COUNTER_UNTIL_NEXT_MODEL_UPDATE: PositiveInt = 5
    # Etikedi config options
    RANDOM_SAMPLE_EVERY: PositiveInt = 10
    TIMEOUT_FOR_WORKER: PositiveInt = 60

    DATASET_NAME: str = "Dataset"
    AMOUNT_OF_FEATURES: int = -1

    @validator('QUERY_STRATEGY_CONFIG')
    def validate_strategy_config(cls, config, values):
        return AlExperimentConfig.validate_strategy_config(config, values)


default_al_config = ActiveLearningConfig()
