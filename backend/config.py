from enum import Enum
from typing import Optional

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# to get a string like this run:
# openssl rand -hex 32

SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "3fb64e315cf5256245416b77fcf0a3853f60a271680a5b9a6a7f8064594c195d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

fake_users_db = {
    "ernst_haft": {
        "username": "ernst_haft",
        "full_name": "Ernst Haft",
        "email": "ernsthaft@example.com",
        "hashed_password": "$2b$12$2TfAuYT9tMAbhc5vRKZs5uLEcUNRtwDPUFuhqDqiRK7XufHV/S4a.",
        "disabled": False,
    },
    "anna_lühse": {
        "username": "anna_lühse",
        "full_name": "Anna Lühse",
        "email": "annalühse@example.com",
        "hashed_password": "$2b$12$0jILJK2b1vIoQCfWcU4U1.6X9M16F68WAQW4.BqsNJ69iiZFc.HAC",
        "disabled": False,
    },
    "mario_nette": {
        "username": "mario_nette",
        "full_name": "Mario Nette",
        "email": "marionette@example.com",
        "hashed_password": "$2b$12$0jILJK2b1vIoQCfWcU4U1.6X9M16F68WAQW4.BqsNJ69iiZFc.HAC",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class ApiTags(Enum):
    Users = 'users'
    Datasets = 'datasets'


openapi_tags = [{
    'name': 'users'
}, {
    'name': 'datasets'
}]

app = FastAPI(openapi_tags=openapi_tags)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
