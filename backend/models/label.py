from pydantic import BaseModel as Schema
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from ..config import Base


class Label(Base):
    __tablename__ = "label"
    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)

    dataset_id = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="labels")

    samples = relationship(
        "Sample",
        secondary="association",
        lazy="subquery",
        cascade="all, delete",
        passive_deletes=True
    )


class BaseLabelSchema(Schema):
    name: str


class LabelDTO(BaseLabelSchema):
    id: int

    class Config:
        orm_mode = True


class CreateLabelDTO(BaseLabelSchema):
    pass
