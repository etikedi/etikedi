from pydantic import (
    confloat as constrained_float,
    conint as constrained_int,
    BaseModel as Schema,
    PositiveFloat,
    PositiveInt,
)

from .al_strategy import QueryStrategyType
from .config import ALModel, QueryStrategyConfig, StoppingCriteria


class AlExperimentConfig(Schema):
    QUERY_STRATEGY: QueryStrategyType = QueryStrategyType.QUERY_INSTANCE_RANDOM
    QUERY_STRATEGY_CONFIG: QueryStrategyConfig = QueryStrategyConfig()
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER
    STOPPING_CRITERIA: StoppingCriteria = StoppingCriteria.ALL_LABELED
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request
