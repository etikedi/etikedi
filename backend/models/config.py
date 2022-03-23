from __future__ import annotations  # necessary for self referencing annotations

from typing import Optional, Union

from pydantic import (
    BaseModel,
    PositiveInt, validator, )

from .al_model import (
    QueryStrategyType,
    QueryInstanceBMDRHolder,
    QueryInstanceGraphDensityHolder,
    QueryInstanceLALHolder,
    QueryInstanceQBCHolder,
    QueryInstanceQUIREHolder,
    QueryInstanceSPALHolder,
    QueryInstanceUncertaintyHolder,
    QueryInstanceRandomHolder,
    QueryExpectedErrorReductionHolder, ALModel, StoppingCriteriaOption,
)
from .battle import AlExperimentConfig


class ActiveLearningConfig(BaseModel):
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
