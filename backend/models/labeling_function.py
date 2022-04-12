from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from ..config import Base
from .datatypes.sample import SampleDTO


class LabelingFunction(Base):
    __tablename__ = "labelingfunction"
    id = Column(Integer, primary_key=True)
    function_body = Column(String(), nullable=False)

    dataset_id = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="labeling_functions")


class LabelingFunctionDTO(BaseModel):
    id: int
    function_body: str

    class Config:
        orm_mode = True

class TestRunResponse(BaseModel):
    result: List[str]
    sample: SampleDTO