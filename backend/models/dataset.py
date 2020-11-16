from pydantic import BaseModel as Schema
from sqlalchemy import Column, Text, String, Integer

from ..config import Base


class Dataset(Base):
    """ Represents a complete dataset. """

    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True, nullable=False)
    feature_names = Column(String(), nullable=True)
    features = Column(Text(), nullable=True)
    config = Column(
        Text(),
        nullable=True,
        # default=json.dumps(dataclasses.asdict(default_al_config)),
    )

    def __repr__(self):
        return 'Dataset "{}" ({})'.format(self.name, self.id)

    def __str__(self):
        return self.name


class BaseDatasetSchema(Schema):
    name: str


# class CreateDataset(BaseDatasetSchema):
#     sample_type: str


class DatasetDTO(BaseDatasetSchema):
    id: int

    class Config:
        orm_mode = True


# class DatasetSchema(ma.Schema):
#     class Meta:
#         fields = ("id", "name")
