from pydantic import BaseModel as Schema
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from ..config import Base


class LabelingFunction(Base):
    __tablename__ = "labelingfunction"
    id = Column(Integer, primary_key=True)
    function_body = Column(String(), nullable=False)

    dataset_id = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="labeling_functions")


class LabelingFunctionDTO(Schema):
    function_body: str

    class Config:
        orm_mode = True