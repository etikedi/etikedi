import uvicorn

from .importing import import_test_datasets
from .config import Base, engine, db, logger
from .models import User, Sample
from .utils import get_password_hash


def create_dummy_users():
    logger.info("Creating dummy users")
    admin = User(
        username="ernst_haft",
        fullname="Ernst Haft",
        email="ernsthaft@example.com",
        password=get_password_hash("adminadmin"),
        roles="admin"
    )
    db.add(admin)

    worker1 = User(
        username="anna_lühse",
        fullname="Anna Lühse",
        email="annalühse@example.com",
        password=get_password_hash("very_secret"),
        roles="worker",
    )
    db.add(worker1)

    worker2 = User(
        username="mario_nette",
        fullname="Mario Nette",
        email="marionette@example.com",
        password=get_password_hash("very_secret"),
        roles="worker",
    )
    db.add(worker2)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    if not db.query(User).count():
        create_dummy_users()
        db.commit()

    if not db.query(Sample).count():
        import_test_datasets()
        db.commit()

    uvicorn.run("backend:app", host="0.0.0.0", reload=True)
