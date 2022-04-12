""" Preprocessing steps for the uci dataset """
import csv
import requests
from pathlib import Path
from zipfile import ZipFile
import os
from scipy.io.arff import loadarff
from sqlalchemy import create_engine
import pandas as pd

from .generic import import_dataset
from .utils import download_archive
from ..config import logger
from ..models import TextSample


def import_uci(uci_dataset_name: str, data_path: Path):
    """
    Downloads uci dataset and transform to generic etikedi-input-format.
    Might throw an exception at some point.
    """
    uci_path = data_path / "uci"
    uci_path.mkdir(parents=True, exist_ok=True)
    uci_url = "https://cloudstore.zih.tu-dresden.de/index.php/s/7BmLjrijGGEcpEE/download?path=/&files="
    uci_datasets_zip = uci_path / "uci_datasets.zip"

    if not uci_datasets_zip.exists():
        logger.info("Downloading uci")
        with uci_datasets_zip.open("wb") as uci_file:
            data_req = requests.get(uci_url)
            if data_req.status_code != 200:
                raise Exception(
                    f"Could not download {uci_path}" f"got code {data_req.status_code}"
                )
            uci_file.write(data_req.content)

    extracted_uci_datasets = uci_path / "extracted"
    extracted_uci_datasets.mkdir(parents=True, exist_ok=True)

    if not any(extracted_uci_datasets.iterdir()):  # only if the directory is empty
        # extract uci zip file
        uci_zip_handle = ZipFile(uci_datasets_zip)

        logger.info("Extracting zip file with uci datasets")
        uci_zip_handle.extractall(path=extracted_uci_datasets)

    extracted_uci_datasets = extracted_uci_datasets / "uci"

    content_zip = str(extracted_uci_datasets / uci_dataset_name) + "_data.csv.zip"

    uci_df = pd.read_csv(str(extracted_uci_datasets / uci_dataset_name) + "_data.csv")
    with ZipFile(content_zip, "w") as content_zip_file:
        for _, row in uci_df.iterrows():
            identifier = str(row["ID"])
            content = str(row["content"])
            content_zip_file.writestr(f"{identifier}.raw", content)

    import_dataset(
        name=uci_dataset_name,
        sample_class=TextSample,
        features=Path(str(extracted_uci_datasets / uci_dataset_name) + "_features.csv"),
        content=Path(str(extracted_uci_datasets / uci_dataset_name) + "_data.csv.zip"),
    )
