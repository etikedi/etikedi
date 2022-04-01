from pathlib import Path

from .cifar import convert_cifar
from .dwtc import convert_dwtc
from .religious_texts import convert_religions_texts
from .uci import import_uci
from ..models import Dataset
from ..config import db, logger

DATA_PATH = (Path(__file__).absolute() / "../../data").resolve()


def import_test_datasets(data_path: Path = None):
    if data_path is None:
        data_path = DATA_PATH
    data_path.mkdir(parents=True, exist_ok=True)
    existing_dataset_names = [d.name for d in db.query(Dataset).all()]
    try:
        if "CIFAR" not in existing_dataset_names:
            convert_cifar(data_path)
    except Exception as e:
        error = e.message if hasattr(e, "message") else str(e)
        logger.warning("Could not import CIFAR dataset. Failed with message: " + error)
    try:
        if "DWTC" not in existing_dataset_names:
            convert_dwtc(data_path)
    except Exception as e:
        error = e.message if hasattr(e, "message") else str(e)
        logger.warning("Could not import dwtc dataset. Failed with message: " + error)

    try:
        if "Religions Texts" not in existing_dataset_names:
            convert_religions_texts(data_path)
    except Exception as e:
        error = e.message if hasattr(e, "message") else str(e)
        logger.warning(
            "Could not import religions_texts dataset. Failed with message: " + error
        )

    uci_datasets = [
        "glass",
        "zoo",
        "HABERMAN",
        "GERMAN",
        "parkinsons",
        "PLANNING",
        "ILPD",
        "flag",
        "DIABETES",
        "FERTILITY",
        "australian",
        "IONOSPHERE",
        "PIMA",
        "adult",
        "HEART",
        "wine",
        "BREAST",
        "abalone",
    ]

    for uci_dataset in uci_datasets:
        try:
            if uci_dataset not in existing_dataset_names:
                logger.info("import uci " + uci_dataset)
                import_uci(uci_dataset, data_path)
            else:
                logger.info("uci " + uci_dataset + " exists already")
        except Exception as e:
            error = e.message if hasattr(e, "message") else str(e)
            logger.warning(
                "Could not import uci dataset "
                + uci_dataset
                + ". Failed with message: "
                + error
            )


if __name__ == "__main__":
    import_test_datasets()
