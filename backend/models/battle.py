from __future__ import annotations

from enum import IntEnum
from typing import List, Tuple, Optional, Union

from pydantic import (
    confloat as constrained_float,
    BaseModel as Schema,
    PositiveInt,
    NonNegativeInt, NonNegativeFloat, validator
)

from .al_strategy import QueryStrategyType
from .config import ALModel, QueryStrategyConfig, StoppingCriteriaOption

ZeroToOne = constrained_float(ge=0, le=1)


class AlExperimentConfig(Schema):
    QUERY_STRATEGY: QueryStrategyType = QueryStrategyType.QUERY_INSTANCE_RANDOM
    QUERY_STRATEGY_CONFIG: QueryStrategyConfig = QueryStrategyConfig()
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER
    STOPPING_CRITERIA_VALUE: Union[None, float, int] = None
    STOPPING_CRITERIA: StoppingCriteriaOption = StoppingCriteriaOption.ALL_LABELED
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request

    @validator('STOPPING_CRITERIA')
    def stopping_criteria_with_option(cls, criteria, values):
        if criteria != StoppingCriteriaOption.ALL_LABELED and (
                'STOPPING_CRITERIA_VALUE' not in values or values['STOPPING_CRITERIA_VALUE'] is None):
            raise ValueError(
                f"If stopping_criteria is not: {StoppingCriteriaOption.ALL_LABELED} the value has to be set")
        return criteria


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
    data_maps: Tuple[str, str]


class Metric(Schema):
    iterations: List  # List[Tuple[Optional[MetricData],Optional[MetricData]]]
