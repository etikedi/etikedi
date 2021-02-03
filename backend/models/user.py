from typing import Optional

from pydantic import BaseModel as Schema
from sqlalchemy import Column, Integer, VARCHAR, Text, Boolean

from ..config import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255), unique=True, nullable=False)
    fullname = Column(VARCHAR(255))
    email = Column(VARCHAR(255))
    roles = Column(Text)
    password = Column(Text)

    is_active = Column(Boolean, default=True, server_default="true", nullable=False)


class BaseUserSchema(Schema):
    username: str
    email: Optional[str] = None
    fullname: Optional[str] = None
    is_active: bool
    roles: str

    class Config:
        orm_mode = True


class BaseUserWithIDSchema(BaseUserSchema):
    id: int


class UserInDB(BaseUserSchema):
    # hashed password
    password: str


class Token(Schema):
    access_token: str
    token_type: str


class UserNewPW(BaseUserSchema):
    # Only for setting first PW or reset PW through admin
    new_password: str
