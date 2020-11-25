from pydantic import BaseModel as Schema
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref

from ..config import Base


class Label(Base):
    __tablename__ = "label"
    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)

    dataset_id = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    dataset = relationship("Dataset", backref=backref("labels"))


class BaseLabelSchema(Schema):
    name: str


class LabelDTO(BaseLabelSchema):
    id: int

    class Config:
        orm_mode = True


class CreateLabelDTO(BaseLabelSchema):
    pass
