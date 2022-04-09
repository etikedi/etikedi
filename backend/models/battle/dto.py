from __future__ import annotations

from enum import IntEnum, Enum
from typing import Optional, List, Tuple, Dict, Union

import numpy as np
import pandas as pd
from altair import UrlData
from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt, validator, root_validator, \
    PositiveInt

from .configs import ZeroToOne
from ..al_model import QueryStrategyType


# metrics / diagrams
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


class Metric(BaseModel):
    iterations: List[Tuple[Optional[MetricIteration], Optional[MetricIteration]]]
    percentage_similar: List[ZeroToOne]


# experiment specific
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
                raise ValueError("Dataframe should contain all keys as column")
        return metric_scores

    @validator("raw_predictions")
    def validate_raw_predictions(cls, raw_predictions):
        if not all(isinstance(col, int) for col in raw_predictions.columns):
            raise ValueError("All columns should be database-ids of samples.")
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
            raise ValueError("Each item should contain all iterations.")
        return values


class MetricsDFKeys(str, Enum):
    Acc = 'Acc',
    F1 = 'F1',
    F1_AUC = 'F1_AUC'
    Precision = 'Precision',
    Recall = 'Recall'
    AvgDistanceLabeled = 'AvgDistanceLabeled'
    AvgDistanceUnLabeled = 'AvgDistanceUnlabeled'


class StateIOValueKeys(str, Enum):
    PERC_LABELED = 'percentage_labeled',
    TIME = 'training_time'
    SAMPLES = 'select_index'


class ExperimentQueueEventType(IntEnum):
    SETUP_COMPLETED = 1
    INFO = 2,
    RESULT = 3


# response_model
class Status(BaseModel):
    class Code(IntEnum):
        IN_SETUP = 0,
        TRAINING = 1,
        COMPLETED = 2

    code: Status.Code
    time: Optional[float] = None  # last reported trainings time


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


class ClassificationBoundariesDTO(BaseModel):
    exp_one_iterations: List[UrlData]
    exp_two_iterations: List[UrlData]
    x_bins: PositiveInt
    y_bins: PositiveInt
    feature_one_name: str
    feature_two_name: str

    class Config:
        arbitrary_types_allowed = True

    @root_validator()
    def validate_all(cls, values):
        exp_one = values['exp_one_iterations']
        exp_two = values['exp_two_iterations']
        if len(exp_one) != len(exp_two):
            raise ValueError('Both experiments should have the same number of iterations.')
        return values


class VectorSpaceDTO(BaseModel):
    exp_one_urls: List[UrlData]
    exp_two_urls: List[UrlData]
    feature_one_name: str
    feature_two_name: str

    class Config:
        arbitrary_types_allowed = True


class DataMapsDTO(BaseModel):
    exp_one_urls: List[UrlData]
    exp_two_urls: List[UrlData]

    class Config:
        arbitrary_types_allowed = True
