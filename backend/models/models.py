import dataclasses
import json

from backend.config import default_al_config
from backend.database import Base
from sqlalchemy import Column, Integer, VARCHAR, Text, Boolean
from sqlalchemy import Float
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, backref


class Association(Base):
    __tablename__ = "association"
    """ The decision of a user to assign a label to a sample. """

    sample_id = Column(Integer, ForeignKey("sample.id"), primary_key=True)
    sample = relationship("Sample", backref="associations")

    label_id = Column(Integer, ForeignKey("label.id"), primary_key=True)
    label = relationship("Label", backref="associations")

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    user = relationship("User", backref="associations")


class Dataset(Base):
    """ Represents a complete dataset. """
    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True, nullable=False)
    feature_names = Column(String(), nullable=True)
    features = Column(Text(), nullable=True)
    config = Column(
        Text(),
        nullable=True,
        default=json.dumps(dataclasses.asdict(default_al_config)),
    )

    # def __repr__(self):
    #     return 'Dataset "{}" ({})'.format(self.name, self.id)
    #
    # def __str__(self):
    #     return self.name


class Flower(Base):
    __tablename__ = "flower"

    id = Column(Integer, primary_key=True)
    sepal_length = Column(Float)
    sepal_width = Column(Float)
    petal_length = Column(Float)
    petal_width = Column(Float)
    label = Column(Integer)


class Label(Base):
    __tablename__ = "label"
    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)

    dataset_id = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    dataset = relationship("Dataset", backref=backref("labels", lazy=True))


class User(Base):
    __tablename__ = "user"
    """
    Simple user model.

    Taken from the [basic example](https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py) of
    [flask-praetorian](https://github.com/dusktreader/flask-praetorian/).
    """

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255))
    roles = Column(Text)
    password = Column(Text)

    is_active = Column(Boolean, default=True, server_default="true")

    # def __str__(self):
    #     return 'User "{}" with roles {}'.format(self.username, self.roles)

    # # The following methods are required by flask_praetorian
    # def is_valid(self):
    #     return self.is_active
    #
    # @property
    # def rolenames(self):
    #     try:
    #         return self.roles.split(",")
    #     except Exception:
    #         return []
    #
    # @classmethod
    # def lookup(cls, username):
    #     return cls.query.filter_by(username=username).one_or_none()
    #
    # @classmethod
    # def identify(cls, id):
    #     return cls.query.get(id)
    #
    # @property
    # def identity(self):
    #     return self.id
