from ..config import db
from ..models import Dataset, Label, AlExperimentConfig, ALBattleConfig, QueryStrategyType, BattlePlotConfig
from ..utils import ValidationError


def validate_else_throw(dataset_id: int, config: ALBattleConfig):
    strategy_with_correct_context(dataset_id, config.exp_configs[0])
    strategy_with_correct_context(dataset_id, config.exp_configs[1])
    validate_feature_names(dataset_id, config.PLOT_CONFIG)


def strategy_with_correct_context(dataset_id: int, config: AlExperimentConfig):
    if config.QUERY_STRATEGY == QueryStrategyType.QUERY_INSTANCE_BMDR or \
            config.QUERY_STRATEGY == QueryStrategyType.QUERY_INSTANCE_LAL:

        number_of_labels = db.query(Label).filter(Label.dataset_id == dataset_id).distinct(Label.name).count()
        if number_of_labels != 2:
            raise ValidationError(
                f"Query strategy ({config.QUERY_STRATEGY}) is implemented for binary classification only,"
                f"but dataset has {number_of_labels} classes.")


def validate_feature_names(dataset_id: int, plot_config: BattlePlotConfig):
    dataset: Dataset = db.get(Dataset, dataset_id)
    if plot_config.FEATURES is None:
        return
    invalid_names = list(filter(lambda name: name not in dataset.feature_names, plot_config.FEATURES))
    if len(invalid_names) > 0:
        raise ValidationError(
            f"Feature names are not part of the dataset: {invalid_names}")
