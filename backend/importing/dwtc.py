""" Preprocessing steps for the DWTC dataset """
import csv
from pathlib import Path
from zipfile import ZipFile

from scipy.io.arff import loadarff
from sqlalchemy import create_engine

from .generic import import_dataset
from .utils import get_or_create_dataset, download_archive
from ..config import app
from ..models import Table


def convert_dwtc_features(source: Path, to: Path) -> None:
    """ Convert the .arff feature file to csv """
    app.logger.info("Converting DWTC features")
    with source.open() as arff_file, to.open("w") as csv_file:
        csv_writer = csv.writer(csv_file)
        data, metadata = loadarff(arff_file)

        feature_names = list(data.dtype.names)
        feature_names[-1] = "LABEL"
        csv_writer.writerow(feature_names)

        for entry in data:
            entry = list(entry)
            entry[0] = int(entry[0])
            csv_writer.writerow(entry)


def convert_dwtc_data(source: Path, to: Path) -> None:
    """ Convert the Sqlite database to a zip """
    dwtc_engine = create_engine(f"sqlite:///{source}")
    cursor = dwtc_engine.execute('SELECT * FROM "table"')

    with ZipFile(to, "w") as zip_file:
        app.logger.info("Converting DWTC data")
        for entry in cursor.fetchall():
            identifier, content = entry[0], entry[7]
            if not content:
                content = ""
            zip_file.writestr(f"{identifier}.raw", content)


def convert_dwtc(data_path: Path):
    dwtc_path = data_path / "dwtc"
    dwtc_path.mkdir(parents=True, exist_ok=True)

    arff_path = dwtc_path / "data.arff"
    database_path = dwtc_path / "data.db"

    if not (arff_path.exists() and database_path.exists()):
        app.logger.info("Downloading DWTC")
        download_archive(
            url="https://cloudstore.zih.tu-dresden.de/index.php/s/wdX6X3t7AwiFdrY/download",
            download_path=data_path / "dwtc.zip",
            target_path=data_path,
        )

    target_csv_path = dwtc_path / "dwtc.csv"
    target_zip_path = dwtc_path / "dwtc.zip"

    if not target_csv_path.exists():
        convert_dwtc_features(source=arff_path, to=target_csv_path)

    if not target_zip_path.exists():
        convert_dwtc_data(source=database_path, to=target_zip_path)

    import_dataset(
        dataset=get_or_create_dataset("DWTC"),
        sample_class=Table,
        features=target_csv_path,
        content=target_zip_path,
    )
