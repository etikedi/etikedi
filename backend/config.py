from dataclasses import dataclass, field

from marshmallow import validate
from marshmallow_dataclass import class_schema

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]


##############################################################################################################
#                                          Active Learning                                                   #
##############################################################################################################


@dataclass
class ALConfig:
    SAMPLING: str = field(
        metadata={
            "validate": validate.OneOf(
                [
                    "random",
                    "uncertainty_lc",
                    "uncertainty_max_margin",
                    "uncertainty_entropy",
                ]
            )
        }
    )
    CLUSTER: str = field(
        metadata={
            "validate": validate.OneOf(
                [
                    "dummy",
                    "random",
                    "MostUncertain_lc",
                    "MostUncertain_max_margin",
                    "MostUncertain_entropy",
                ]
            )
        }
    )
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: float = field(
        metadata={"validate": validate.Range(min=0.5, max=1)}
    )
    UNCERTAINTY_RECOMMENDATION_RATIO: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    STOPPING_CRITERIA_UNCERTAINTY: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    STOPPING_CRITERIA_ACC: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    STOPPING_CRITERIA_STD: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    USER_QUERY_BUDGET_LIMIT: float = field(metadata={"validate": validate.Range(min=0)})
    RANDOM_SEED: float = field(metadata={"validate": validate.Range(min=-1)})
    NR_QUERIES_PER_ITERATION: int = field(metadata={"validate": validate.Range(min=0)})
    N_JOBS: int = field(metadata={"validate": validate.Range(min=-1)})
    NR_LEARNING_ITERATIONS: int = field(metadata={"validate": validate.Range(min=0)})
    ALLOW_RECOMMENDATIONS_AFTER_STOP: bool
    WITH_UNCERTAINTY_RECOMMENDATION: bool
    WITH_CLUSTER_RECOMMENDATION: bool
    WITH_SNUBA_LITE: bool

    RANDOM_SAMPLE_EVERY: int = field(metadata={"validate": validate.Range(min=5)})


ALConfigSchema = class_schema(ALConfig)

default_al_config = ALConfig(
    SAMPLING="uncertainty_max_margin",
    CLUSTER="MostUncertain_max_margin",
    NR_QUERIES_PER_ITERATION=100,
    WITH_UNCERTAINTY_RECOMMENDATION=True,
    WITH_CLUSTER_RECOMMENDATION=True,
    WITH_SNUBA_LITE=False,
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS=0,
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD=0.99,
    UNCERTAINTY_RECOMMENDATION_RATIO=0.01,
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED=0.8,
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE=0.3,
    ALLOW_RECOMMENDATIONS_AFTER_STOP=True,
    STOPPING_CRITERIA_UNCERTAINTY=0,
    STOPPING_CRITERIA_ACC=0,
    STOPPING_CRITERIA_STD=0,
    USER_QUERY_BUDGET_LIMIT=2000,
    RANDOM_SEED=-1,
    N_JOBS=-1,
    NR_LEARNING_ITERATIONS=200000,
    RANDOM_SAMPLE_EVERY=10,
)
