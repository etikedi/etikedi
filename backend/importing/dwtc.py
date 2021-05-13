""" Preprocessing steps for the DWTC dataset """
import csv
import requests
from pathlib import Path
from zipfile import ZipFile

from scipy.io.arff import loadarff
from sqlalchemy import create_engine

from .generic import import_dataset
from .utils import download_archive
from ..config import logger
from ..models import Table


def _convert_dwtc_features(source: Path, to: Path) -> None:
    """ Convert the .arff feature file to csv """
    logger.info("Converting DWTC features")
    with source.open() as arff_file, to.open("w") as csv_file:
        csv_writer = csv.writer(csv_file)
        data, metadata = loadarff(arff_file)

        feature_names = list(data.dtype.names)
        if "ID" not in feature_names[0]:
            raise Exception(".arff malformed expected first column to be ID")
        feature_names[-1] = "LABEL"
        csv_writer.writerow(feature_names)

        for entry in data:
            entry = list(entry)
            # ensure ids are integer
            entry[0] = int(entry[0])
            if isinstance(entry[-1], bytes):
                entry[-1] = entry[-1].decode()
            csv_writer.writerow(entry)


def _convert_dwtc_data(source: Path, to: Path) -> None:
    """ Convert the Sqlite database to a zip """
    dwtc_engine = create_engine(f"sqlite:///{source}")
    cursor = dwtc_engine.execute('SELECT * FROM "table"')

    with ZipFile(to, "w") as zip_file:
        logger.info("Converting DWTC data")
        for entry in cursor.fetchall():
            identifier, content = entry[0], entry[7]
            if not content:
                content = ""
            zip_file.writestr(f"{identifier}.raw", content)


def convert_dwtc(data_path: Path):
    """
    Download dwtc dataset and transform to generic etikedi-input-format.
    Might throw an exception at some point.
    """
    dwtc_path = data_path / "dwtc"
    dwtc_path.mkdir(parents=True, exist_ok=True)

    database_file_name = "data.db"
    arff_file_name = "2017_feature_selection.arff"

    arff_path = dwtc_path / arff_file_name
    database_path = dwtc_path / database_file_name
    # download database and .arff files
    url = "https://cloudstore.zih.tu-dresden.de/index.php/s/f33QRxXteWbxReP/download?path=/&files="
    if not arff_path.exists() or not database_path.exists():
        logger.info("Downloading DWTC")
        with database_path.open("wb") as db_file:
            data_req = requests.get(url + database_file_name)
            if data_req.status_code != 200:
                raise Exception(f"Could not download {database_file_name} from {url + database_file_name} "
                                f"got code {data_req.status_code}")
            db_file.write(data_req.content)

        with arff_path.open("wb") as arff_file:
            arff_req = requests.get(url + arff_file_name)
            if arff_req.status_code != 200:
                raise Exception(f"Could not download {arff_file_name} from {url + arff_file_name} "
                                f"got code {arff_req.status_code}")
            arff_file.write(arff_req.content)

    target_csv_path = dwtc_path / "dwtc.csv"
    target_zip_path = dwtc_path / "dwtc.zip"

    if not target_csv_path.exists():
        _convert_dwtc_features(source=arff_path, to=target_csv_path)

    if not target_zip_path.exists():
        _convert_dwtc_data(source=database_path, to=target_zip_path)

    import_dataset(
        name="DWTC",
        sample_class=Table,
        features=target_csv_path,
        content=target_zip_path,
    )
