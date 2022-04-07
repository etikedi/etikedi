from typing import List, Dict, Union

from fastapi import APIRouter, HTTPException, status, Query

from ..battle_mode import BattleAnalyzer, BattleManager, plotting, Persistence, ExperimentMetaPersistence
from ..config import db, logger
from ..models import (
    Dataset,
    ALBattleConfig,
    Metric,
    ChartReturnSchema,
    Status,
    QueryStrategyType,
    Label,
    ValidStrategiesReturnSchema
)
from ..utils import ValidationError

battle_router = APIRouter()


@battle_router.get("/valid_strategies/{dataset_id}", response_model=ValidStrategiesReturnSchema)
async def valid_strategies(dataset_id: int):
    "Return all al-strategies and their configuration options that are applicable for this dataset."
    number_of_labels = db.query(Label).filter(Label.dataset_id == dataset_id).distinct(Label.name).count()
    valid: List[QueryStrategyType] = list(
        filter(lambda strategy: number_of_labels == 2 or not strategy.only_binary_classification(), QueryStrategyType))
    return ValidStrategiesReturnSchema(
        strategies={strategy: strategy.get_config_schema().schema_json() for strategy in valid}
    )


@battle_router.post("/start")
async def start_battle(battle_config: ALBattleConfig, dataset_id: int):
    """Return the generated experiment-id."""
    _assert_dataset_exists(dataset_id)
    # start process
    try:
        experiment_id = BattleManager.create_and_start(dataset_id, battle_config)
        return experiment_id
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@battle_router.get("/{experiment_id}/status", response_model=Status)
async def is_finish(experiment_id: int):
    """ If an experiment started returns the last measured training-iteration-time
    @return
         0 if the experiments are still in setup.
         1 if at least one is still training, additionally returns a time in seconds.
         2 if both are successfully completed.
                """
    if BattleManager.has_finished_manager(experiment_id):
        return Status(code=Status.Code.COMPLETED)
    _assert_active_manager_exists(experiment_id)
    return BattleManager.get_active_manager(experiment_id).get_status()


@battle_router.delete("/{experiment_id}")
async def terminate(experiment_id: int):
    """ Terminate an active experiment or remove a finished one.
        This will not affect the persistence of experiments.
    """
    if BattleManager.has_active_manager(experiment_id) or BattleManager.has_finished_manager(experiment_id):
        BattleManager.remove_or_terminate(experiment_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No manager for this experiment ID")


@battle_router.get("/{experiment_id}/diagrams", response_model=ChartReturnSchema)
async def get_diagrams(experiment_id: int):
    """Return all diagrams."""
    _assert_completed(experiment_id)
    logger.info("Requesting diagrams for experiment: " + str(experiment_id))
    manager = BattleManager.get_or_create_finished_manager(experiment_id)
    # create diagrams

    # learning curve: line chart x=iterations, y = accuracy
    learning_curve = plotting.learning_curve_plot(manager.get_learning_curve_data())

    # confidence: histogram, x=confidence, y=occurrence
    confidence_plots = plotting.confidence_histograms(manager.get_confidence_his_data())

    # data_maps: scatter plot, x=variability, y=confidence
    data_maps = plotting.data_maps(manager.get_data_map_data())

    # vector_space: scatter plot x=feature_1, y=feature_2
    vector_space_plots = plotting.vector_space(manager.get_vector_space_data())

    classification_boundaries = plotting.classification_boundaries(manager.get_classification_boundary_data())

    return ChartReturnSchema(
        acc=learning_curve,
        conf=confidence_plots,
        data_maps=data_maps,
        vector_space=vector_space_plots,
        classification_boundaries=classification_boundaries
    )


@battle_router.get("/{experiment_id}/metrics", response_model=Metric)
async def get_metrics(experiment_id: int):
    """Return all metrics."""
    _assert_completed(experiment_id)
    return BattleManager.get_or_create_finished_manager(experiment_id).get_metrics()


@battle_router.get("/persisted", response_model=Union[Dict[int, ExperimentMetaPersistence], Dict[int, List]])
async def get_persisted(by_dataset: bool = Query(default=False, alias='by-dataset')):
    """
    Return meta-information about all experiments that are stored and can be loaded:
        Dict with experiment_id -> ExperimentMetaPersistence.
    If by_dataset is true. the dict-keys are dataset_ids and the values are a list of all experiments for this dataset:
        Dict with dataset_id -> List[experiment_id -> ExperimentMetaPersistence].
    """
    persisted: Dict[int, ExperimentMetaPersistence] = Persistence.persisted_experiments
    if not by_dataset:
        return persisted
    by_dataset_dict: Dict[int, List[Dict[int, ExperimentMetaPersistence]]] = {}
    for (exp_id, exp_meta) in persisted.items():
        if exp_meta.dataset_id not in by_dataset_dict:
            by_dataset_dict[exp_meta.dataset_id] = []
        by_dataset_dict[exp_meta.dataset_id].append({exp_id: exp_meta})
    return by_dataset_dict


@battle_router.get("/persisted/{experiment_id}")
async def load_persisted(experiment_id: int):
    """ Load the results of a persisted experiment, in order to generate diagrams and metrics.
    @return the meta information about this experiment.
     """
    _assert_experiment_persisted(experiment_id)
    manager: BattleAnalyzer = Persistence.load_finished_experiments(experiment_id)
    BattleManager.set_finished_manager(manager)
    return Persistence.persisted_experiments[experiment_id]


@battle_router.post("/persisted/{experiment_id}")
async def store_experiment(experiment_id: int):
    _assert_completed(experiment_id)
    Persistence.store_finished_experiments(
        experiment_id,
        BattleManager.get_or_create_finished_manager(experiment_id))


@battle_router.delete("/persisted/{experiment_id}")
async def delete_persisted(experiment_id: int):
    _assert_experiment_persisted(experiment_id)
    Persistence.delete(experiment_id)


# Assertions

def _assert_dataset_exists(dataset_id: int):
    if not db.query(Dataset).get(dataset_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found for id: {}.".format(dataset_id)
        )


def _assert_experiment_persisted(experiment_id: int):
    if experiment_id not in Persistence.persisted_experiments:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Experiment {experiment_id} is not persisted.")


def _assert_active_manager_exists(experiment_id: int):
    if not BattleManager.has_active_manager(experiment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No manager for ID {experiment_id}.")


def _assert_finished_manager_exists(experiment_id: int):
    if not BattleManager.has_finished_manager(experiment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No manager for ID {experiment_id}.")


def _assert_completed(experiment_id):
    if BattleManager.has_finished_manager(experiment_id):
        return
    _assert_active_manager_exists(experiment_id)
    try:
        BattleManager.get_active_manager(experiment_id).assert_finished()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
