import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# set access parameters for server and database
server_username = "root"
server_password = "admin"
server_ipaddress = os.getenv('DATABASE_URL', default='localhost')
server_port = "5432"
db_name = "aergia"

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
