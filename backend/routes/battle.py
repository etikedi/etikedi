from fastapi import APIRouter, HTTPException, status

from ..battle_mode import ExperimentManager, plotting
from ..models import AlExperimentConfig, Metric, ChartReturnSchema, Status

battle_router = APIRouter()


@battle_router.post("/start")
async def start_battle(dataset_id: int, config1: AlExperimentConfig, config2: AlExperimentConfig):
    """Return if training started successfully."""

    # start process
    ExperimentManager(dataset_id, config1, config2).start()


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
    data_maps = plotting.data_maps(manager.get_data_map_data())

    return ChartReturnSchema(acc=learning_curve, conf=confidence_plots, data_maps=data_maps)


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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=getattr(e, 'message', 'Not started'))


def _assert_completed(dataset_id):
    try:
        ExperimentManager.get_manager(dataset_id).assert_finished()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=getattr(e, 'message', 'Not started'))
