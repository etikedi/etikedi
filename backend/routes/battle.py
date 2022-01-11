import altair as alt
from fastapi import APIRouter, HTTPException, status


from ..battle_mode import ExperimentManager
from ..models import AlExperimentConfig, Metric

battle_router = APIRouter()


@battle_router.post("/start")
async def start_battle(dataset_id: int, config1: AlExperimentConfig, config2: AlExperimentConfig):
    """Return if training started successfully."""

    # start process
    ExperimentManager(dataset_id, config1, config2).start()


@battle_router.get("/is_finish")
async def is_finish(dataset_id: int):
    """ If an experiment started returns the last measured training-iteration-time
    @return
                -1 if both are finished
                -2 if no (new) data is available
                time in seconds if at least one has finished one iteration
                """
    _assert_manager_exists(dataset_id)

    # estimate remaining time
    # return in seconds
    return ExperimentManager.get_manager(dataset_id).get_status()


@battle_router.get("/get_diagrams")
async def get_diagrams(dataset_id: int):
    """Return all diagrams."""
    _assert_manager_exists(dataset_id)

    # create diagrams
    # return in list
    # TODO


    return {"acc": "", "variability":""}


@battle_router.get("/get_metrics", response_model=Metric)
async def get_metrics(dataset_id: int):
    """Return all metrics."""
    _assert_manager_exists(dataset_id)

    try:
        metrics = ExperimentManager.get_manager(dataset_id).get_metrics()
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=getattr(e, 'message', "No Manager"))


def _assert_manager_exists(dataset_id: int):
    if not ExperimentManager.has_manager(dataset_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No manager for ID {dataset_id}")
