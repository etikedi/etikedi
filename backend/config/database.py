from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# inside the backend folder
database_path = Path(__file__).parent.parent.absolute() / 'test.db'
server_name = "postgres"
server_password = "admin"
server_address = "localhost"
server_port = "5432"
db_name = "postgres"

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}:{}/{}" \
    .format(server_name, server_password, server_address, server_port, db_name)
SQLALCHEMY_TRACK_MODIFICATIONS = False

engine = create_engine(
    SQLALCHEMY_DATABASE_URI
    # connect_args={
    #    "check_same_thread": SQLALCHEMY_TRACK_MODIFICATIONS,
    #    "timeout": 30
    # },
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
