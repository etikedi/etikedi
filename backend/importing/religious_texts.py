""" Preprocessing steps for the Religions Texts dataset """
import codecs
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from .generic import import_dataset
from .utils import download_archive
from ..config import logger
from ..models import TextSample


def convert_religions_texts_features(source: Path, to: Path) -> None:
    logger.info("Converting Religions Texts features")
    features = pd.read_csv(source, delimiter=",")

    label_names = []

    for index, book in features.iterrows():
        label = book[0][:book[0].rfind("_")]
        label_names.append(label)

    features["LABEL"] = label_names
    features.drop(columns='Unnamed: 0', inplace=True)

    features.to_csv(to, index_label="ID")


def convert_religions_texts_data(source: Path, to: Path) -> None:
    """ Convert the text file to a zip """
    with ZipFile(to, "w") as zip_file, codecs.open(source, "r", "ISO-8859-1") as source_file:
        logger.info("Converting Religions Texts data")
        identifier = 0
        for row in source_file:
            if is_number(row):
                continue
            if not row:
                row = ""
            zip_file.writestr(f"{identifier}.raw", row)
            identifier += 1


def convert_religions_texts(data_path: Path):
    religions_texts_path = data_path / "religions_texts"
    religions_texts_path.mkdir(parents=True, exist_ok=True)

    feature_path = religions_texts_path / "AllBooks_baseline_DTM_Labelled.csv"
    text_path = religions_texts_path / "Complete_data .txt"

    if not (feature_path.exists() and text_path.exists()):
        logger.info("Downloading Religions Texts")
        download_archive(
            url="https://archive.ics.uci.edu/ml/machine-learning-databases/00512/AsianReligionsData.zip",
            download_path=religions_texts_path / "ReligionsData.zip",
            target_path=religions_texts_path,
        )

    target_csv_path = religions_texts_path / "religions_texts.csv"
    target_zip_path = religions_texts_path / "religions_texts.zip"

    if not target_csv_path.exists():
        convert_religions_texts_features(source=feature_path, to=target_csv_path)

    if not target_zip_path.exists():
        convert_religions_texts_data(source=text_path, to=target_zip_path)

    import_dataset(
        name="Religions Texts",
        sample_class=TextSample,
        features=target_csv_path,
        content=target_zip_path,
    )


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
