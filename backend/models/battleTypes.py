from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Dict

import pandas as pd
from pydantic import BaseModel, root_validator


class MetricsDFKeys(str, Enum):
    Acc = 'Acc',
    F1 = 'F1',
    F1_AUC = 'F1_AUC'
    Precision = 'Precision',
    Recall = 'Recall'
    AvgDistanceLabeled = 'AvgDistanceLabeled'
    AvgDistanceUnLabeled = 'AvgDistanceUnlabeled'


class MapKeys(str, Enum):
    PERC_LABELED = 'percentage_labeled',
    TIME = 'training_time'
    SAMPLES = 'select_index'


class EventType(IntEnum):
    SETUP_COMPLETED = 1
    INFO = 2,
    RESULT = 3


# Dataclasses
@dataclass
class ClassificationBoundariesDTO:
    reduced_features: pd.DataFrame
    exp_one_iterations: List[pd.DataFrame]
    exp_two_iterations: List[pd.DataFrame]


class DataMapsDTO(BaseModel):
    # list-entry = iteration, rows = Samples, columns = metric-scores
    exp_one_data: List[pd.DataFrame]
    exp_two_data: List[pd.DataFrame]

    class Config:
        arbitrary_types_allowed = True

    @root_validator()
    def validate_all(cls, values):
        exp_one = values['exp_one_data']
        exp_two = values['exp_two_data']
        if len(exp_one) != len(exp_two):
            raise ValueError('Both experiments should have the same number of iterations.')
        for exp in [exp_one, exp_two]:
            for frame in exp:
                if any(col not in ['Confidence', 'Variability', 'Correctness', 'SampleID'] for col in frame.columns) \
                        or len(frame.columns) != 4:
                    raise ValueError('Dataframe had bad columns')
        return values
