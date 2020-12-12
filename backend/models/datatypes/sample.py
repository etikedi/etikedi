import base64
from typing import Union, Optional, List

from pydantic import BaseModel as Schema
from sqlalchemy import ForeignKey, Column, Integer, VARCHAR
from sqlalchemy.orm import backref, relationship

from .. import LabelDTO
from ...config import Base


class Sample(Base):
    """
    Base class for samples.

    Uses joined table inheritance to enable polymorphic fetching of
    concrete samples of a specific data table. Documentation about how
    this works can be found in the [docs](https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/inheritance.html)
    """

    # TODO: Add associations as backref?

    __tablename__ = "sample"

    id = Column(Integer, primary_key=True)

    dataset_id = Column(Integer, ForeignKey(
        "dataset.id", ondelete="CASCADE"), nullable=False)
    dataset = relationship("Dataset", backref=backref("items", lazy=True))

    labels = relationship(
        "Label",
        lazy="subquery",
        secondary="association",
        back_populates="samples",
        cascade="all, delete",
        passive_deletes=True
    )

    associations = relationship(
        "Association",
        back_populates='sample'
    )

    # Saves concrete type of data in this sample
    type = Column(VARCHAR(10))

    content: Union[str, bytes]

    __mapper_args__ = {"polymorphic_identity": "sample",
                       "polymorphic_on": "type"}

    def ensure_string_content(self) -> None:
        """ Converts the content to a base64 encoded string if it is binary """
        if not isinstance(self.content, str):
            self.content = base64.b64encode(self.content).decode()

    def __str__(self):
        return "Sample {} in {}".format(self.id, self.dataset)

    def __repr__(self):
        return str(self)


class SampleDTO(Schema):
    id: int
    dataset_id: int
    type: str
    content: str

    class Config:
        orm_mode = True


class SampleDTOwLabel(SampleDTO):
    labels: Optional[List[LabelDTO]] = None


class UnlabelDTO(Schema):
    label_id: int
    all: bool = True
