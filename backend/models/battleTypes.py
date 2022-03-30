from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Dict

import pandas as pd

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
