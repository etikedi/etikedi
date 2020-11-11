from typing import Optional

from pydantic import BaseModel


class DatasetBase(BaseModel):
    id: int
    name: str


class AssociationBase(BaseModel):
    sample_id: int
    label_id: int
    user_id: int


class LabelSchema(BaseModel):
    id: int
    name: str


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
