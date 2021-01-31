from enum import Enum

from pydantic import (
    confloat as constrained_float,
    conint as constrained_int,
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


class InitialBatchSamplingMethod(Enum):
    Furthest = "furthest"
    Random = "random"


class Classifier(Enum):
    RF = 'RF'
    SVM = 'SVM'
    NB = 'NB'
    MLP = 'MLP'
    DT = 'DT'


class DistanceMetric(Enum):
    Euclidean = 'euclidean'
    Cosine = 'cosine'


ZeroToOne = constrained_float(ge=0, le=1)
OneHalfToOne = constrained_float(ge=0.5, le=1)
LargerNegativeOne = constrained_float(ge=-1)


class ActiveLearningConfig(Schema):
    # AL options requried by the `active_learning` module
    ALLOW_RECOMMENDATIONS_AFTER_STOP: bool = True
    BATCH_MODE: bool = False
    CLASSIFIER: Classifier = Classifier.RF
    CLUSTER: ClusterMethod = ClusterMethod.MostUncertain_max_margin
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: ZeroToOne = 0.3
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: ZeroToOne = 0.8
    DISTANCE_METRIC: DistanceMetric = DistanceMetric.Euclidean
    GENERATE_NOISE: bool = True
    HYPERCUBE: bool = True
    INITIAL_BATCH_SAMPLING_ARG: constrained_int(ge=0, le=2000) = 10
    INITIAL_BATCH_SAMPLING_HYBRID_FURTHEST: ZeroToOne = 0.4
    INITIAL_BATCH_SAMPLING_HYBRID_FURTHEST_LAB: ZeroToOne = 0
    INITIAL_BATCH_SAMPLING_HYBRID_PRED_UNITY: ZeroToOne = 0
    INITIAL_BATCH_SAMPLING_HYBRID_UNCERT: ZeroToOne = 0.4
    INITIAL_BATCH_SAMPLING_METHOD: InitialBatchSamplingMethod = InitialBatchSamplingMethod.Furthest
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: ZeroToOne = 0
    NEW_SYNTHETIC_PARAMS: bool = False
    NR_LEARNING_ITERATIONS: PositiveInt = 200000
    NR_QUERIES_PER_ITERATION: PositiveInt = 100
    N_JOBS: LargerNegativeOne = -1
    PLOT_EVOLUTION: bool = False
    RANDOM_SEED: PositiveInt = 1
    SAMPLING: SamplingMethod = SamplingMethod.Uncertainty_max_margin
    STATE_ARGSECOND_PROBAS: bool = True
    STATE_ARGTHIRD_PROBAS: bool = True
    STATE_DIFF_PROBAS: bool = False
    STATE_DISTANCES: bool = False
    STATE_DISTANCES_LAB: bool = True
    STATE_DISTANCES_UNLAB: bool = True
    STATE_INCLUDE_NR_FEATURES: bool = True
    STATE_PREDICTED_CLASS: bool = False
    STATE_PREDICTED_UNITY: bool = False
    STATE_UNCERTAINTIES: bool = False
    STOPPING_CRITERIA_ACC: ZeroToOne = 0
    STOPPING_CRITERIA_STD: ZeroToOne = 0
    STOPPING_CRITERIA_UNCERTAINTY: ZeroToOne = 0
    STOP_AFTER_MAXIMUM_ACCURACY_REACHED: bool = False
    TEST_FRACTION: ZeroToOne = 0.3
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: OneHalfToOne = 0.99
    UNCERTAINTY_RECOMMENDATION_RATIO: ZeroToOne = 0.01
    USER_QUERY_BUDGET_LIMIT: PositiveFloat = 2000
    VARIABLE_DATASET: bool = True
    WITH_CLUSTER_RECOMMENDATION: bool = True
    WITH_SNUBA_LITE: bool = False
    WITH_UNCERTAINTY_RECOMMENDATION: bool = True

    # Aergia config options
    RANDOM_SAMPLE_EVERY: PositiveInt = 10
    TIMEOUT_FOR_WORKER: PositiveInt = 60

    def add_default_options(self, dataset_id: int):
        self.DATASET_NAME = str(dataset_id)
        self.AMOUNT_OF_FEATURES = -1


default_al_config = ActiveLearningConfig()
