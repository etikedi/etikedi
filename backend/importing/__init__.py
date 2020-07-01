from pathlib import Path
from .dwtc import convert_dwtc
from .religious_texts import import_religions_texts
from .cifar import convert_cifar
from .generic import import_dataset

DATA_PATH = (Path(__file__).absolute() / '../../data').resolve()


def import_test_datasets():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    convert_cifar(DATA_PATH)
    convert_dwtc(DATA_PATH)
    # import_religions_texts(DATA_PATH)


if __name__ == '__main__':
    import_test_datasets()
