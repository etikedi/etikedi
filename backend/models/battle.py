from __future__ import annotations

from enum import IntEnum
from typing import List, Tuple, Optional, Union, Dict

import numpy as np
import pandas as pd
from pydantic import (
    confloat as constrained_float,
    BaseModel,
    PositiveInt,
    NonNegativeInt, NonNegativeFloat, validator,
    ValidationError, Field, root_validator
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
from .battleTypes import MetricsDFKeys

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
        invalid_properties = list(filter(lambda key: key not in ConfigSchema.schema()['properties'], raw_config.keys()))
        if len(invalid_properties) > 0:
            raise ValueError(f"For config: {ConfigSchema.schema_json()} "
                             f"some properties did not match: {invalid_properties}")
        try:
            config = ConfigSchema(**raw_config)
            return config
        except ValidationError as e:
            raise ValueError("Config did not match strategy: " + str(e))


class BattlePlotConfig(BaseModel):
    FEATURES: Optional[Tuple[str, str]] = None


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


class Status(BaseModel):
    class Code(IntEnum):
        IN_SETUP = 0,
        TRAINING = 1,
        COMPLETED = 2

    code: Status.Code
    time: Optional[float] = None  # last reported trainings time


class MetaData(BaseModel):
    time: NonNegativeFloat  # model training time in seconds
    percentage_labeled: ZeroToOne
    sample_ids: List[NonNegativeInt]


class MetricScoresIteration(BaseModel):
    Acc: ZeroToOne
    F1: ZeroToOne
    F1_AUC: NonNegativeFloat
    Precision: ZeroToOne
    Recall: ZeroToOne
    AvgDistanceLabeled: NonNegativeFloat
    AvgDistanceUnLabeled: NonNegativeFloat

    @staticmethod
    def of(series: pd.Series):
        return MetricScoresIteration(
            Acc=series[MetricsDFKeys.Acc],
            F1=series[MetricsDFKeys.F1],
            F1_AUC=series[MetricsDFKeys.F1_AUC],
            Precision=series[MetricsDFKeys.Precision],
            Recall=series[MetricsDFKeys.Recall],
            AvgDistanceLabeled=series[MetricsDFKeys.AvgDistanceLabeled],
            AvgDistanceUnLabeled=series[MetricsDFKeys.AvgDistanceUnLabeled]
        )


class MetricIteration(BaseModel):
    meta: MetaData
    metrics: MetricScoresIteration


# A list over all iterations (max of both experiments)
# For each iteration for both experiments: the metric scores and the metadata
class Metric(BaseModel):
    iterations: List[Tuple[Optional[MetricIteration], Optional[MetricIteration]]]
    percentage_similar: List[ZeroToOne]


class ValidStrategiesReturnSchema(BaseModel):
    """
    Represents all valid strategies for this dataset.
    Json represents the config options as BaseModel.schema_json()
    """
    strategies: Dict[QueryStrategyType, str]


class ChartReturnSchema(BaseModel):
    acc: str
    conf: Tuple[List[str], List[str]]
    data_maps: Tuple[List[str], List[str]]
    vector_space: Tuple[List[str], List[str]]
    classification_boundaries: Tuple[List[str], List[str]]


class ExperimentResults(BaseModel):
    # 3D data-frame: row = iteration, column = sample, value = tuple of confidence per class
    # columns = SampleID
    raw_predictions: pd.DataFrame
    # columns = 0..n index of randomly generated samples
    cb_predictions: pd.DataFrame
    # row = iteration, columns = list(MetricDFKeys)
    metric_scores: pd.DataFrame
    # A list of all SampleIDs that were initially labeled
    initially_labeled: List[int]
    # SampleID -> range(classes)
    # For all test-samples is stored which index of classes would be the right one
    correct_label_as_idx: Dict[int, int]
    # Each entry is one iteration
    meta_data: List[MetaData]
    # List of all possible labels as used by the al_model
    classes: Union[List[str], np.ndarray]

    class Config:
        arbitrary_types_allowed = True

    @validator("metric_scores")
    def validate_metric_scores(cls, metric_scores):
        for key in MetricsDFKeys:
            if key not in metric_scores.columns:
                raise ValidationError("Dataframe should contain all keys as column")
        return metric_scores

    @validator("raw_predictions")
    def validate_raw_predictions(cls, raw_predictions):
        if not all(isinstance(col, int) for col in raw_predictions.columns):
            raise ValidationError("All columns should be database-ids of samples.")
        return raw_predictions

    @root_validator()
    def validate_all(cls, values):
        if 'raw_predictions' not in values or 'cb_predictions' not in values or 'metric_scores' not in values:
            return values
        raw_predictions = values['raw_predictions']
        cb_predictions = values['cb_predictions']
        metric_scores = values['metric_scores']
        meta_data = values['meta_data']
        if len(raw_predictions) != len(cb_predictions) \
                or len(cb_predictions) != len(metric_scores) \
                or len(metric_scores) != len(meta_data):
            raise ValidationError("Each item should contain all iterations.")
        return values
