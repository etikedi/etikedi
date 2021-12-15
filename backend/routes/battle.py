import altair as alt
from fastapi import APIRouter, HTTPException, status
from vega_datasets import data

from ..battle_mode import ExperimentManager
from ..models import AlExperimentConfig

battle_router = APIRouter()


@battle_router.post("/start")
async def start_battle(dataset_id: int, config1: AlExperimentConfig, config2: AlExperimentConfig):
    """Return if training started successfully."""

    # start process
    ExperimentManager(dataset_id, config1, config2).run()
    return True


@battle_router.get("/is_finish")
async def is_finish(dataset_id: int):
    """Return training status."""
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
    chart1 = (
        alt.Chart(data.cars.url)
            .mark_point()
            .encode(x="Horsepower:Q", y="Miles_per_Gallon:Q", color="Origin:N")
    )

    chart2 = (
        alt.Chart(data.anscombe.url)
            .mark_point()
            .encode(x="X:Q", y="X:Q", color="Series:N")
    )

    return {"acc": chart1.to_json(), "variability": chart2.to_json()}


@battle_router.get("/get_metrics")
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
