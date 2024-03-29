from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from . import LabelDTO
from ..config import Base


class Association(Base):
    __tablename__ = "association"
    """ The decision of a user to assign a label to a sample. """

    sample_id = Column(Integer, ForeignKey("sample.id"), primary_key=True)
    sample = relationship("Sample", back_populates="associations")

    label_id = Column(Integer, ForeignKey("label.id"), primary_key=True)
    label = relationship("Label", backref="associations")

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", backref="associations")

    is_current = Column(Boolean, default=True, server_default="true", nullable=False)

    __mapper_args__ = {"confirm_deleted_rows": False}


class AssociationBase(BaseModel):
    sample_id: int
    label_id: int
    user_id: int


class AssociationCurrentLabel(BaseModel):
    label: LabelDTO
    is_current: bool

    class Config:
        orm_mode = True
