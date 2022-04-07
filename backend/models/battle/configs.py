from __future__ import annotations

from typing import Union, Optional, Tuple

from pydantic import (
    BaseModel,
    Field,
    validator,
    ValidationError,
    PositiveInt,
    confloat as constrained_float
)

from ..al_model import (
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


class AlExperimentConfig(BaseModel):
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
    ] = Field(default=QUERY_STRATEGY.get_default_config(), discriminator='query_type')
    AL_MODEL: ALModel = ALModel.RANDOM_FOREST_CLASSIFIER

    @validator('QUERY_STRATEGY_CONFIG', pre=True)
    def validate_strategy_config(cls, raw_config, values):
        strategy = values['QUERY_STRATEGY']
        ConfigSchema = strategy.get_config_schema()
        properties = raw_config.keys() if hasattr(raw_config, 'keys') else raw_config.dict().keys()
        invalid_properties = list(filter(lambda key: key not in ConfigSchema.schema()['properties'], properties))
        if len(invalid_properties) > 0:
            raise ValueError(f"For config: {ConfigSchema.schema_json()} "
                             f"some properties did not match: {invalid_properties}")
        try:
            config = ConfigSchema(**raw_config)
            return config
        except ValidationError as e:
            raise ValueError("Config did not match strategy: " + str(e))


class ClassificationBoundariesConfig(BaseModel):
    NBR_OF_RANDOM_SAMPLE: PositiveInt = 100
    MAX_X_BINS: PositiveInt = 20
    MAX_Y_BINS: PositiveInt = 20


class BattlePlotConfig(BaseModel):
    FEATURES: Optional[Tuple[str, str]] = None
    CLASSIFICATION_BOUNDARIES: ClassificationBoundariesConfig = ClassificationBoundariesConfig()


class ALBattleConfig(BaseModel):
    exp_configs: Tuple[AlExperimentConfig, AlExperimentConfig]
    STOPPING_CRITERIA_VALUE: Union[None, float, int] = None
    STOPPING_CRITERIA: StoppingCriteriaOption = StoppingCriteriaOption.ALL_LABELED
    BATCH_SIZE: PositiveInt = 5  # number of samples suggested per request
    RANDOM_SEED: int = 42  # seed for generating train-test-split
    TRAIN_TEST_SPLIT: ZeroToOne = 0.3
    # percentage of trainings-set or exactly one sample per class
    INITIALLY_LABELED: ZeroToOne = 0.05
    PLOT_CONFIG: BattlePlotConfig = BattlePlotConfig()

    @validator('STOPPING_CRITERIA')
    def stopping_criteria_with_option(cls, criteria, values):
        if criteria != StoppingCriteriaOption.ALL_LABELED and (
                'STOPPING_CRITERIA_VALUE' not in values or values['STOPPING_CRITERIA_VALUE'] is None):
            raise ValueError(
                f"If stopping_criteria is not: {StoppingCriteriaOption.ALL_LABELED} the value has to be set")
        return criteria
