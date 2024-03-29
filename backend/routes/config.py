import json

from fastapi import APIRouter, HTTPException, status, Depends

from ..utils import get_current_active_user
from ..worker import manager
from ..config import db
from ..models import Dataset, ActiveLearningConfig, User

config_router = APIRouter()


@config_router.get("/", response_model=ActiveLearningConfig)
async def get_dataset_config(dataset_id: int, user: User = Depends(get_current_active_user)):
    """ Return the current configuration for the given dataset. """
    if user.roles != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the authorization to request this! Ask your admin!"
        )

    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No config found."
        )

    return dataset.get_config()


@config_router.post("/", response_model=ActiveLearningConfig)
async def change_dataset_config(dataset_id: int,
                                config: ActiveLearningConfig,
                                user: User = Depends(get_current_active_user)):
    """ Update the configuration for the given dataset. Implies a restart of the AL process. Currently not working. """
    if user.roles != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the authorization to change this! Ask your admin!"
        )

    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No dataset found."
        )

    dataset.set_config(config)
    db.commit()

    worker = manager.get(dataset)
    if worker:
        worker.restart_process()

    return dataset.get_config()
