from typing import Optional

from pydantic import BaseModel as Schema
from sqlalchemy import Column, Integer, VARCHAR, Text, Boolean

from ..config import Base


class User(Base):
    __tablename__ = "user"
    """
    Simple user model.

    Taken from the [basic example](https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py) of
    [flask-praetorian](https://github.com/dusktreader/flask-praetorian/).
    """

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255))
    fullname = Column(VARCHAR(255))
    email = Column(VARCHAR(255))
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


class BaseUserSchema(Schema):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(BaseUserSchema):
    hashed_password: str


class Token(Schema):
    access_token: str
    token_type: str
