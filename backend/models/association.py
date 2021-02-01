from pydantic import BaseModel as Schema
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..config import Base


class Association(Base):
    __tablename__ = "association"
    """ The decision of a user to assign a label to a sample. """

    sample_id = Column(Integer, ForeignKey("sample.id"), primary_key=True)
    sample = relationship("Sample", back_populates="associations")

    label_id = Column(Integer, ForeignKey("label.id"), primary_key=True)
    label = relationship("Label",   backref="associations")

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    user = relationship("User", backref="associations")


class AssociationBase(Schema):
    sample_id: int
    label_id: int
    user_id: int
