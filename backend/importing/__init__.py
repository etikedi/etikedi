from pathlib import Path

from .cifar import convert_cifar
from .dwtc import convert_dwtc
from .religious_texts import convert_religions_texts
from ..models import Dataset
from ..config import db, logger

DATA_PATH = (Path(__file__).absolute() / "../../data").resolve()


def import_test_datasets(data_path: Path = None):
    if data_path is None:
        data_path = DATA_PATH
    if db.query(Dataset).count():
        return
    data_path.mkdir(parents=True, exist_ok=True)
    try:
        convert_cifar(data_path)
    except Exception as e:
        error = e.message if hasattr(e, 'message') else str(e)
        logger.warning("Could not import CIFAR dataset. Failed with message: " + error)
    try:
        convert_dwtc(data_path)
    except Exception as e:
        error = e.message if hasattr(e, 'message') else str(e)
        logger.warning("Could not import dwtc dataset. Failed with message: " + error)
    try:
        convert_religions_texts(data_path)
    except Exception as e:
        error = e.message if hasattr(e, 'message') else str(e)
        logger.warning("Could not import religions_texts dataset. Failed with message: " + error)


if __name__ == "__main__":
    import_test_datasets()
