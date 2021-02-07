import base64
from typing import Union, Optional, List

from pydantic import BaseModel as Schema, validator
from sqlalchemy import ForeignKey, Column, Integer, VARCHAR
from sqlalchemy.orm import relationship

from .. import AssociationCurrentLabel
from ...config import Base


class Sample(Base):
    """
    Base class for samples.

    Uses joined table inheritance to enable polymorphic fetching of
    concrete samples of a specific data table. Documentation about how
    this works can be found in the [docs](https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/inheritance.html)
    """

    __tablename__ = "sample"

    id = Column(Integer, primary_key=True)

    dataset_id = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    dataset = relationship("Dataset", back_populates="samples", lazy=True)

    labels = relationship(
        "Label",
        lazy="subquery",
        secondary="association",
        back_populates="samples",
        passive_deletes=True
    )

    associations = relationship(
        "Association",
        cascade="all, delete",
        back_populates='sample'
    )

    # Saves concrete type of data in this sample
    type = Column(VARCHAR(10))

    content: Union[str, bytes]

    __mapper_args__ = {"polymorphic_identity": "sample",
                       "polymorphic_on": "type"}


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

    @validator("content", pre=True)
    def ensure_string_content(cls, content):
        """ Converts the content to a base64 encoded string if it is binary """
        if not isinstance(content, str):
            content = base64.b64encode(content).decode()
        return content


class SampleDTOwLabel(SampleDTO):
    associations: Optional[List[AssociationCurrentLabel]] = None

    # only return current labels for filtered Samples, remove old labels
    @validator("associations")
    def current_associations(cls, associations):
        current_associations = associations
        for association in associations:
            if not association.is_current:
                current_associations.remove(association)
        return current_associations


class UnlabelDTO(Schema):
    label_id: Optional[int]
    all: bool = False
