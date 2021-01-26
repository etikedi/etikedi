import json

from fastapi import APIRouter, HTTPException, status

from ..worker import manager
from ..config import db
from ..models import Dataset, ActiveLearningConfig

config_router = APIRouter()


@config_router.get("/", response_model=ActiveLearningConfig)
async def get_dataset_config(dataset_id: int):
    """ Return the current configuration for the given dataset. """
    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No config found."
        )

    return dataset.get_config()


@config_router.post("/", response_model=ActiveLearningConfig)
async def change_dataset_config(dataset_id: int, config: ActiveLearningConfig):
    """ Update the configuration for the given dataset. Implies a restart of the AL process. Currently not working. """
    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No dataset found."
        )

    dataset.set_config(config)
    db.commit()

    worker = manager.get(dataset_id)
    worker.restart_process(json.loads(dataset.config))

    return dataset.get_config()
