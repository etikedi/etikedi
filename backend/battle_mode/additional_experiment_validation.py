from ..config import db
from ..models import Dataset, Label, AlExperimentConfig, ALBattleConfig, QueryStrategyType, BattlePlotConfig, \
    QMeasureType
from ..utils import ValidationError


def validate_else_throw(dataset_id: int, config: ALBattleConfig):
    non_binary_classification_restrictions(dataset_id, config.exp_configs[0])
    non_binary_classification_restrictions(dataset_id, config.exp_configs[1])
    validate_feature_names(dataset_id, config.PLOT_CONFIG)


def non_binary_classification_restrictions(dataset_id: int, config: AlExperimentConfig):
    number_of_labels = db.query(Label).filter(Label.dataset_id == dataset_id).distinct(Label.name).count()
    if config.QUERY_STRATEGY.only_binary_classification() and number_of_labels != 2:
        raise ValidationError(
            f"Query strategy ({config.QUERY_STRATEGY}) is implemented for binary classification only,"
            f"but dataset has {number_of_labels} classes.")

    if config.QUERY_STRATEGY == QueryStrategyType.QUERY_INSTANCE_UNCERTAINTY:
        if config.QUERY_STRATEGY_CONFIG.measure == QMeasureType.DISTANCE_TO_BOUNDARY:
            raise ValidationError(
                f"{QMeasureType.DISTANCE_TO_BOUNDARY} is not applicable for datasets with more than two label."
            )


def validate_feature_names(dataset_id: int, plot_config: BattlePlotConfig):
    dataset: Dataset = db.get(Dataset, dataset_id)
    if plot_config.FEATURES is None:
        return
    invalid_names = list(filter(lambda name: name not in dataset.feature_names, plot_config.FEATURES))
    if len(invalid_names) > 0:
        raise ValidationError(
            f"Feature names are not part of the dataset: {invalid_names}")
