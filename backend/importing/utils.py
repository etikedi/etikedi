import shutil
from pathlib import Path

import requests
from sqlalchemy.orm.exc import NoResultFound

from ..config import db
from ..models import Dataset


def get_or_create_dataset(name):
    try:
        dataset = Dataset.query.filter(Dataset.name == name).one()
    except NoResultFound:
        dataset = Dataset(name=name)
        db.session.add(dataset)

    return dataset


def download_archive(url: str, download_path: Path, target_path: Path):
    with download_path.open('wb') as f:
        f.write(requests.get(url).content)

    shutil.unpack_archive(download_path, target_path)
    download_path.unlink()
