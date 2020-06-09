from sqlalchemy.orm.exc import NoResultFound
from ..config import db
from ..models import Dataset


def get_or_create_dataset(name):
    try:
        dataset = Dataset.query.filter(Dataset.name == name).one()
    except NoResultFound:
        dataset = Dataset(name=name)
        db.session.add(dataset)
        db.session.commit()

    return dataset
