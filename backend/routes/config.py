import dataclasses
import json

from fastapi import APIRouter, Depends, HTTPException, status
from marshmallow import ValidationError
from pydantic import dataclasses
from sqlalchemy.orm import Session

from ..active_learning_process import manager
from ..config import get_db
from ..models import Dataset, ALConfigSchema

config_router = APIRouter()


@config_router.get("/")
async def get_dataset_config(dataset_id: int, db: Session = Depends(get_db)):
    """ Return the current configuration for the given dataset. """
    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No config found."
        )

    return json.loads(dataset.config)


@config_router.post("/")
async def change_dataset_config(dataset_id: int, items, db: Session = Depends(get_db)):
    """ Update the configuration for the given dataset. Implies a restart of the AL process. Currently not working. """
    dataset = db.query(Dataset).get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset found."
        )

    try:
        new_config = ALConfigSchema().load(
            {k.upper(): v for k, v in items}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.messages
        )

    dataset.config = json.dumps(dataclasses.asdict(new_config))
    db.commit()

    manager.restart_with_config(dataset, json.loads(dataset.config))

    return None, 204
