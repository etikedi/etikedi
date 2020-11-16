import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..active_learning_process import manager
from ..config import get_db
from ..models import Dataset, ActiveLearningConfig

config_router = APIRouter()


@config_router.get("/", response_model=ActiveLearningConfig)
async def get_dataset_config(dataset_id: int, db: Session = Depends(get_db)):
    """ Return the current configuration for the given dataset. """
    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No config found."
        )

    return ActiveLearningConfig(**json.loads(dataset.config))


@config_router.post("/")
async def change_dataset_config(dataset_id: int, config: ActiveLearningConfig, db: Session = Depends(get_db)):
    """ Update the configuration for the given dataset. Implies a restart of the AL process. Currently not working. """
    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset found."
        )

    dataset.config = json.dumps(config.dict())
    db.commit()

    manager.restart_with_config(dataset, json.loads(dataset.config))

    return None, 204
