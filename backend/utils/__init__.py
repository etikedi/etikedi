import time
from functools import wraps
from typing import List
from ..config import logger

from .dataset import *
from .labels import *
from .users import *
from .exceptions import *


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


# zip two lists of unequal size with None as fill
def zip_unequal(l1: List, l2: List):
    diff = len(l1) - len(l2)
    if diff == 0:
        return zip(l1, l2)
    elif diff < 0:
        return zip(l1 + ([None] * abs(diff)), l2)
    else:
        return zip(l1, l2 + ([None] * diff))
