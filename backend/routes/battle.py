import json
import altair as alt
from vega_datasets import data

from fastapi import APIRouter, HTTPException, status, Depends

from ..utils import get_current_active_user
from ..worker import manager
from ..config import db
from ..models import Dataset, ActiveLearningConfig, User

config_router = APIRouter()

remaining_time = 11


@config_router.post("/al-wars/{dataset_id}/start")
async def start_battle(
    dataset_id: int, config1: ActiveLearningConfig, config2: ActiveLearningConfig
):
    """Return if training started successfully."""

    # start process

    return True


@config_router.get("/al-wars/{dataset_id}/is_finish")
async def is_finish(dataset_id: int):
    """Return training status."""

    # estimate remaining time
    # return in seconds

    return 15


@config_router.get("/al-wars/{dataset_id}/get_diagrams")
async def get_diagrams(dataset_id: int):
    """Return all diagrams."""

    # create diagrams
    # return in list

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


@config_router.get("/al-wars/{dataset_id}/get_metrics")
async def get_metrics(dataset_id: int):
    """Return all metrics."""

    return {}
