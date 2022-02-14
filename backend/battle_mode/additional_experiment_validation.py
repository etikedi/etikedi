from ..utils import ValidationError
from ..models import Label, AlExperimentConfig, QueryStrategyType
from ..config import db


def validate_config(dataset_id: int, config: AlExperimentConfig):
    strategy_with_correct_context(dataset_id, config)


def strategy_with_correct_context(dataset_id: int, config: AlExperimentConfig):
    if config.QUERY_STRATEGY == QueryStrategyType.QUERY_INSTANCE_BMDR or \
            config.QUERY_STRATEGY == QueryStrategyType.QUERY_INSTANCE_LAL:

        number_of_labels = db.query(Label).filter(Label.dataset_id == dataset_id).distinct(Label.name).count()
        if number_of_labels != 2:
            raise ValidationError(
                f"Query strategy ({config.QUERY_STRATEGY}) is implemented for binary classification only,"
                f"but dataset has {number_of_labels} classes.")
