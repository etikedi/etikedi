from __future__ import annotations

from enum import Enum, IntEnum


class MetricsDFKeys(str, Enum):
    Acc = 'Acc',
    F1 = 'F1',
    Precision = 'Precision',
    Recall = 'Recall'


class MapKeys(str, Enum):
    PERC_LABELED = 'percentage_labeled',
    TIME = 'training_time'
    SAMPLES = 'select_index'


class EventType(IntEnum):
    SETUP_COMPLETED = 1
    INFO = 2,
    RESULT = 3
