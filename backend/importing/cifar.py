import json
import pickle
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image as PillowImage

from .utils import get_or_create_dataset, download_archive
from ..config import db, app
from ..models import Image, Sample, Label

files = [
    'data_batch_1',
    # 'data_batch_2',
    # 'data_batch_3',
    # 'data_batch_4',
    # 'data_batch_5'
]


def download_cifar(data_path: Path):
    if (data_path / 'cifar-10-batches-py').exists():
        return

    app.logger.info('Downloading CIFAR...')
    download_archive(
        url='http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz',
        download_path=data_path / 'cifar-10-python.tar.gz',
        target_path=data_path
    )


def convert_cifar_to_png(pixels) -> bytes:
    """
    A list where the first third are the red values, the second thirds the green values and the last
    third the blue values
    """
    image = PillowImage.new('RGB', (32, 32))
    pixel_iterator = zip(*np.array_split(pixels, 3))
    image.putdata(list(pixel_iterator))

    stream = BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def convert_cifar_to_features(pixels) -> str:
    """ Converts the color values of a CIFAR image into a json string. """
    red, green, blue = np.array_split(pixels, 3)
    return json.dumps({
        'red': list(map(int, red)),
        'green': list(map(int, green)),
        'blue': list(map(int, blue))
    })


def import_cifar(data_path: Path):
    cifar = get_or_create_dataset(name='CIFAR-10')
    if Sample.query.filter(Sample.dataset == cifar).count():
        return

    download_cifar(data_path)

    for file in files:
        app.logger.info('Importing {}'.format(file))
        with (data_path / 'cifar-10-batches-py' / file).open('rb') as f:
            data = pickle.load(f, encoding='bytes')

        all_pixels = data[b'data']
        all_filenames = map(lambda x: x.decode(), data[b'filenames'])

        for name, pixels in zip(all_filenames, all_pixels):
            sample = Image()
            sample.dataset = cifar
            sample.name = name
            sample.content = convert_cifar_to_png(pixels)
            sample.features = convert_cifar_to_features(pixels)

            db.session.add(sample)
        db.session.commit()

    labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    db.session.add_all(
        Label(dataset=cifar, name=label_name)
        for label_name in labels
    )
    db.session.commit()
