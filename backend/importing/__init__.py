from pathlib import Path
from .dwtc import import_dwtc
from .religious_texts import import_religions_texts
from .cifar import import_cifar
from .generic import import_dataset


DATA_PATH = (Path(__file__).absolute() / '../../data').resolve()


def import_test_datasets():
    # import_cifar(DATA_PATH)
    import_dwtc(DATA_PATH)
    # import_religions_texts(DATA_PATH)


if __name__ == '__main__':
    import_test_datasets()
