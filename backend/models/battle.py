from __future__ import annotations

from typing import Dict, List, Tuple, Optional

from pydantic import (
    confloat as constrained_float,
    conint as constrained_int,
    BaseModel as Schema,
    PositiveFloat,
    PositiveInt,
)

from .al_strategy import QueryStrategyType
from .config import ALModel, QueryStrategyConfig, StoppingCriteria

ZeroToOne = constrained_float(gt=0, le=1)


class AlExperimentConfig(Schema):
    QUERY_STRATEGY: QueryStrategyType = QueryStrategyType.QUERY_INSTANCE_RANDOM
    QUERY_STRATEGY_CONFIG: QueryStrategyConfig = QueryStrategyConfig()
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER
    STOPPING_CRITERIA: StoppingCriteria = StoppingCriteria.ALL_LABELED
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request


class MetricData(Schema):
    accuracy: ZeroToOne
    time: PositiveInt
    percentage_labeled: ZeroToOne
    sample_ids: List[PositiveInt]


class Metric(Schema):
    iterations: Dict[int, Tuple[Optional[MetricData], Optional[MetricData]]] = {}
