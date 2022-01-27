from __future__ import annotations

from enum import IntEnum
from typing import List, Tuple, Optional

from pydantic import (
    confloat as constrained_float,
    BaseModel as Schema,
    PositiveInt,
    NonNegativeInt, NonNegativeFloat
)

from .al_strategy import QueryStrategyType
from .config import ALModel, QueryStrategyConfig, StoppingCriteria

ZeroToOne = constrained_float(ge=0, le=1)


class AlExperimentConfig(Schema):
    QUERY_STRATEGY: QueryStrategyType = QueryStrategyType.QUERY_INSTANCE_RANDOM
    QUERY_STRATEGY_CONFIG: QueryStrategyConfig = QueryStrategyConfig()
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER
    STOPPING_CRITERIA: StoppingCriteria = StoppingCriteria.ALL_LABELED
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request


class Status(Schema):
    class Code(IntEnum):
        IN_SETUP = 0,
        TRAINING = 1,
        COMPLETED = 2

    code: Status.Code
    time: Optional[float] = None  # last reported trainings time


class MetricData(Schema):
    time: NonNegativeFloat  # model training time in seconds
    percentage_labeled: ZeroToOne
    sample_ids: List[NonNegativeInt]


class ChartReturnSchema(Schema):
    acc: str
    conf: Tuple[List[str], List[str]]


class Metric(Schema):
    iterations: List  # List[Tuple[Optional[MetricData],Optional[MetricData]]]
