import os

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# set access parameters for server and database
from starlette.requests import Request
from .logger import logger

server_username = "root"
server_password = "admin"
server_ipaddress = os.getenv('DATABASE_URL', default='localhost')
server_port = "5432"
db_name = "etikedi"

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}:{}/{}" \
    .format(server_username, server_password, server_ipaddress, server_port, db_name)

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={
        "connect_timeout": 30
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db: SessionLocal = next(get_db())


async def automatic_transaction(request: Request, call_next):
    """Wrap all data-modifying requests in transaction"""
    if request.method.lower() in ("post", "put", "patch", "delete"):
        try:
            response = await call_next(request)
        except SQLAlchemyError as e:
            logger.warning('Rollback of current transaction')
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response = await call_next(request)

    return response
