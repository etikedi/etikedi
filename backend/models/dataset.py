import json
from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, Text, String, Integer, JSON
from sqlalchemy.orm import relationship

from . import default_al_config, ActiveLearningConfig
from .label import LabelDTO
from ..config import Base


@dataclass
class DatasetStatistics:
    total_samples: int
    labelled_samples: int
    features: int
    labels: int


class Dataset(Base):
    """ Represents a complete dataset. """

    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True, nullable=False)
    feature_names = Column(String(), nullable=True)
    features = Column(Text(), nullable=True)
    config = Column(
        JSON,
        nullable=True,
        default=json.dumps(default_al_config.dict(), default=lambda x: x.value),
    )

    labeling_functions = relationship("LabelingFunction", cascade="all, delete", back_populates="dataset")
    samples = relationship("Sample", cascade="all, delete", back_populates="dataset")
    labels = relationship("Label", cascade="all, delete", back_populates="dataset")

    statistics: DatasetStatistics

    def __repr__(self):
        return 'Dataset "{}" ({})'.format(self.name, self.id)

    def __str__(self):
        return self.name

    def get_config(self) -> ActiveLearningConfig:
        return ActiveLearningConfig(**json.loads(self.config))

    def set_config(self, config: ActiveLearningConfig) -> None:
        self.config = json.dumps(config.dict(), default=lambda x: x.value)


class BaseDatasetSchema(BaseModel):
    name: str


class DatasetDTO(BaseDatasetSchema):
    id: int
    labels: List[LabelDTO]

    statistics: Optional[DatasetStatistics]

    class Config:
        orm_mode = True

# class DatasetWithStatisticsDTO(DatasetDTO):
#     statistics: DatasetStatistics

# class DatasetSchema(ma.Schema):
#     class Meta:
#         fields = ("id", "name")
