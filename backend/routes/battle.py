from typing import List

from fastapi import APIRouter, HTTPException, status

from ..battle_mode import ExperimentManager, plotting
from ..config import db
from ..models import (
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


@battle_router.get("/valid_strategies", response_model=ValidStrategiesReturnSchema)
async def valid_strategies(dataset_id: int):
    number_of_labels = db.query(Label).filter(Label.dataset_id == dataset_id).distinct(Label.name).count()
    valid: List[QueryStrategyType] = list(
        filter(lambda strategy: number_of_labels != 2 or not strategy.only_binary_classification(), QueryStrategyType))
    return ValidStrategiesReturnSchema(
        strategies={strategy: strategy.get_config_schema().schema_json() for strategy in valid}
    )


@battle_router.post("/start")
async def start_battle(dataset_id: int, battle_config: ALBattleConfig):
    """Return if training started successfully."""

    # start process
    try:
        ExperimentManager(dataset_id, battle_config).start()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@battle_router.get("/status", response_model=Status)
async def is_finish(dataset_id: int):
    """ If an experiment started returns the last measured training-iteration-time
    @return
                -1 if both are finished
                -2 if no (new) data is available
                time in seconds if at least one has finished one iteration
                """
    _assert_started(dataset_id)
    return ExperimentManager.get_manager(dataset_id).get_status()


@battle_router.get("/get_diagrams", response_model=ChartReturnSchema)
async def get_diagrams(dataset_id: int):
    """Return all diagrams."""
    _assert_completed(dataset_id)
    manager = ExperimentManager.get_manager(dataset_id)
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


@battle_router.get("/get_metrics", response_model=Metric)
async def get_metrics(dataset_id: int):
    """Return all metrics."""
    _assert_completed(dataset_id)
    return ExperimentManager.get_manager(dataset_id).get_metrics()


def _assert_manager_exists(dataset_id: int):
    if not ExperimentManager.has_manager(dataset_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No manager for ID {dataset_id}.")


def _assert_started(dataset_id):
    _assert_manager_exists(dataset_id)
    try:
        ExperimentManager.get_manager(dataset_id).assert_started()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


def _assert_completed(dataset_id):
    try:
        ExperimentManager.get_manager(dataset_id).assert_finished()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
