from __future__ import annotations

from enum import IntEnum
from typing import List, Tuple, Optional, Union, Dict

from pydantic import (
    confloat as constrained_float,
    BaseModel as Schema,
    PositiveInt,
    NonNegativeInt, NonNegativeFloat, validator,
    ValidationError
)

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
    QueryExpectedErrorReductionHolder,
    ALModel,
    StoppingCriteriaOption
)

ZeroToOne = constrained_float(ge=0, le=1)


class AlExperimentConfig(Schema):
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

    @validator('QUERY_STRATEGY_CONFIG', pre=True)
    def validate_strategy_config(cls, raw_config, values):
        strategy = values['QUERY_STRATEGY']
        ConfigSchema = strategy.get_config_schema()
        invalid_properties = list(filter(lambda key: key not in ConfigSchema.schema()['properties'], raw_config.keys()))
        if len(invalid_properties) > 0:
            raise ValueError(f"For config: {ConfigSchema.schema_json()} "
                             f"some properties did not match: {invalid_properties}")
        try:
            config = ConfigSchema(**raw_config)
            return config
        except ValidationError as e:
            raise ValueError("Config did not match strategy: " + str(e))


class BattlePlotConfig(Schema):
    FEATURES: Optional[Tuple[str, str]] = None


class ALBattleConfig(Schema):
    exp_configs: Tuple[AlExperimentConfig, AlExperimentConfig]
    STOPPING_CRITERIA_VALUE: Union[None, float, int] = None
    STOPPING_CRITERIA: StoppingCriteriaOption = StoppingCriteriaOption.ALL_LABELED
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request
    PLOT_CONFIG: BattlePlotConfig = BattlePlotConfig()

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


class Metric(Schema):
    iterations: List  # List[Tuple[Optional[MetricData],Optional[MetricData]]]


class ValidStrategiesReturnSchema(Schema):
    """
    Represents all valid strategies for this dataset.
    Json represents the config options as Schema.schema_json()
    """
    strategies: Dict[QueryStrategyType, str]


class ChartReturnSchema(Schema):
    acc: str
    conf: Tuple[List[str], List[str]]
    data_maps: Tuple[str, str]
    vector_space: Tuple[List[str], List[str]]
