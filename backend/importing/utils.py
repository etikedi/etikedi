import shutil
from pathlib import Path
from sqlalchemy.orm import Session

import requests
from sqlalchemy.orm.exc import NoResultFound

from ..models import Dataset


def get_or_create_dataset(name, db: Session):
    try:
        return db.query(Dataset).filter(Dataset.name == name).one()
    except NoResultFound:
        dataset = Dataset(name=name)
        db.add(dataset)
        db.commit()


def download_archive(url: str, download_path: Path, target_path: Path, db: Session):
    with download_path.open("wb") as f:
        f.write(requests.get(url).content)

    shutil.unpack_archive(download_path, target_path)
    download_path.unlink()
