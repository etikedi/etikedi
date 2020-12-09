import csv
import pickle
from io import BytesIO
from itertools import product
from pathlib import Path
from typing import List
from zipfile import ZipFile

import numpy as np
from PIL import Image as PillowImage

from ..config import db
from .generic import import_dataset
from .utils import download_archive, get_or_create_dataset
from ..config import logger
from ..models import Image

CIFAR_FILES = [
    "data_batch_1",
    # 'data_batch_2',
    # 'data_batch_3',
    # 'data_batch_4',
    # 'data_batch_5'
]


def convert_cifar_to_png(pixels) -> bytes:
    """
    A list where the first third are the red values, the second thirds the green values and the last
    third the blue values
    """
    image = PillowImage.new("RGB", (32, 32))
    pixel_iterator = zip(*np.array_split(pixels, 3))
    image.putdata(list(pixel_iterator))

    stream = BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def get_cifar_meta(path: Path) -> List[str]:
    with path.open('rb') as f:
        raw_meta = pickle.load(f, encoding="bytes")

    label_names = raw_meta[b'label_names']
    return [s.decode() for s in label_names]


def convert_cifar(data_path: Path):
    cifar_path = data_path / "cifar-10-batches-py"

    if not cifar_path.exists():
        logger.info("Downloading CIFAR...")
        download_archive(
            url="http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
            download_path=data_path / "cifar-10-python.tar.gz",
            target_path=data_path,
        )

    target_csv_path = cifar_path / "cifar.csv"
    target_zip_path = cifar_path / "cifar.zip"

    if not (target_csv_path.exists() and target_zip_path.exists()):
        with ZipFile(target_zip_path.open("wb"), "w") as zip_file, target_csv_path.open(
                "w"
        ) as csv_file:
            identifier = 1

            meta = get_cifar_meta(cifar_path / 'batches.meta')

            csv_writer = csv.writer(csv_file)
            colors = ["red", "green", "blue"]
            color_features = [
                f"{color}{index}"
                for color, index in product(colors, range(1, 1024 + 1))
            ]
            feature_names = ["ID"] + color_features + ["LABEL"]
            csv_writer.writerow(feature_names)

            for file_index, file in enumerate(CIFAR_FILES, 1):
                logger.info(f"Converting CIFAR {file_index}/{len(CIFAR_FILES)}")

                with (cifar_path / file).open("rb") as f:
                    data = pickle.load(f, encoding="bytes")

                for pixels, label in zip(data[b"data"], data[b"labels"]):
                    zip_file.writestr(f"{identifier}.raw", convert_cifar_to_png(pixels))
                    csv_writer.writerow([identifier] + list(pixels) + [meta[label]])
                    identifier += 1
    else:
        logger.info("Skip converting CIFAR as it is already present")

    import_dataset(
        name="CIFAR",
        sample_class=Image,
        features=target_csv_path,
        content=target_zip_path,
    )
