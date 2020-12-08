import json
from typing import List
from pydantic import BaseModel as Schema
from sqlalchemy import Column, Text, String, Integer

from . import default_al_config, ActiveLearningConfig
from .label import LabelDTO
from ..config import Base


class Dataset(Base):
    """ Represents a complete dataset. """

    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True, nullable=False)
    feature_names = Column(String(), nullable=True)
    features = Column(Text(), nullable=True)
    config = Column(
        Text(),
        nullable=True,
        default=json.dumps(default_al_config.dict(), default=lambda x: x.value),
    )

    def __repr__(self):
        return 'Dataset "{}" ({})'.format(self.name, self.id)

    def __str__(self):
        return self.name

    def get_config(self) -> ActiveLearningConfig:
        return ActiveLearningConfig(**json.loads(self.config))

    def set_config(self, config: ActiveLearningConfig) -> None:
        self.config = json.dumps(config.dict(), default=lambda x: x.value)


class BaseDatasetSchema(Schema):
    name: str


class DatasetDTO(BaseDatasetSchema):
    id: int
    labels: List[LabelDTO]

    class Config:
        orm_mode = True


# class DatasetSchema(ma.Schema):
#     class Meta:
#         fields = ("id", "name")
