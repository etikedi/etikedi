from enum import Enum

from pydantic import (
    confloat as constrained_float,
    BaseModel as Schema,
    PositiveFloat,
    PositiveInt,
)


class SamplingMethod(Enum):
    Random = "random"
    Uncertainty_lc = "uncertainty_lc"
    Uncertainty_max_margin = "uncertainty_max_margin"
    Uncertainty_entropy = "uncertainty_entropy"


class ClusterMethod(Enum):
    Dummy = "dummy"
    Random = "random"
    MostUncertain_lc = "MostUncertain_lc"
    MostUncertain_max_margin = "MostUncertain_max_margin"
    MostUncertain_entropy = "MostUncertain_entropy"


ZeroToOne = constrained_float(ge=0, le=1)
OneHalfToOne = constrained_float(ge=0.5, le=1)
LargerNegativeOne = constrained_float(ge=-1)


class ActiveLearningConfig(Schema):
    SAMPLING: SamplingMethod = SamplingMethod.Uncertainty_max_margin
    CLUSTER: ClusterMethod = ClusterMethod.MostUncertain_max_margin
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: ZeroToOne = 0
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: OneHalfToOne = 0.99
    UNCERTAINTY_RECOMMENDATION_RATIO: ZeroToOne = 0.01
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: ZeroToOne = 0.8
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: ZeroToOne = 0.3
    STOPPING_CRITERIA_UNCERTAINTY: ZeroToOne = 0
    STOPPING_CRITERIA_ACC: ZeroToOne = 0
    STOPPING_CRITERIA_STD: ZeroToOne = 0
    USER_QUERY_BUDGET_LIMIT: PositiveFloat = 2000
    N_JOBS: LargerNegativeOne = -1
    RANDOM_SEED: PositiveInt = 1
    NR_QUERIES_PER_ITERATION: PositiveInt = 100
    NR_LEARNING_ITERATIONS: PositiveInt = 200000
    ALLOW_RECOMMENDATIONS_AFTER_STOP: bool = True
    WITH_UNCERTAINTY_RECOMMENDATION: bool = True
    WITH_CLUSTER_RECOMMENDATION: bool = True
    WITH_SNUBA_LITE: bool = False

    RANDOM_SAMPLE_EVERY: PositiveInt = 10
    TIMEOUT_FOR_WORKER: PositiveInt = 60


default_al_config = ActiveLearningConfig()
