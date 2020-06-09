import json
from io import BytesIO
from pathlib import Path
import pickle
import numpy as np
from PIL import Image as PillowImage
from ..config import db
from ..models import Image
from .utils import get_or_create_dataset

DATA_PATH = Path(__file__).parent.parent / 'data/cifar-10-batches-py'
files = [
    'data_batch_1',
    'data_batch_2',
    'data_batch_3',
    'data_batch_4',
    'data_batch_5'
]


def unpickle(path: str) -> dict:
    with open(path, 'rb') as fo:
        return pickle.load(fo, encoding='bytes')


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


cifar = get_or_create_dataset(name='CIFAR-10')

for file in files:
    print('Importing {}'.format(file))
    data = unpickle(DATA_PATH / file)
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
