import csv
from pathlib import Path

from .generic import import_dataset
from .utils import download_archive, get_or_create_dataset
from ..config import app
from ..models import Text, Sample


def download_religions_texts(data_path):
    if (data_path / 'AsianReligionsData').exists():
        return

    app.logger.info('Downloading Religions Texts...')
    download_archive(
        url='https://archive.ics.uci.edu/ml/machine-learning-databases/00512/AsianReligionsData.zip',
        download_path=data_path / 'AsianReligiousData.zip',
        target_path=data_path / 'AsianReligionsData'
    )


def import_religions_texts(data_path: Path):
    religions_texts = get_or_create_dataset('Religious texts')
    if Sample.query.filter(Sample.dataset == religions_texts).count():
        app.logger.info('Skip Religions Texts...')
        return
    download_religions_texts(data_path)

    feature_path = data_path / 'AsianReligionsData/AllBooks_baseline_DTM_Labelled.csv'
    text_path = data_path / 'AsianReligionsData/Complete_data .txt'
    content_attribute = 'data'  # Should not be a feature
    
    app.logger.info('Importing Religions Texts...')
    with feature_path.open() as feature_file, text_path.open(encoding='latin-1') as text_file:
        features_names, *all_features = list(csv.reader(feature_file))
        texts = list(text_file)[1::2]
    
        if len(texts) != len(all_features):
            raise ValueError('Number of features does not match the number of texts')
    
        samples = []
        for features, text in zip(all_features, texts):
            sample = {feature: value for feature, value in zip(features_names, features)}
            sample[content_attribute] = text
            samples.append(sample)
    app.logger.info('Done Religions Texts...')
