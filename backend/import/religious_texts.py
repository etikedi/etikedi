""" Preprocessing steps for the DWTC dataset """
import csv
from pathlib import Path
from sqlalchemy.orm.exc import NoResultFound

from .import_dataset import import_dataset
from ..config import db
from ..models import Text, Dataset

DATA_PATH = Path(__file__).parent / 'AsianReligionsData'
feature_path = DATA_PATH / 'AllBooks_baseline_DTM_Labelled.csv'
text_path = DATA_PATH / '/Complete_data .txt'
content_attribute = 'data'  # Should not be a feature

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

dataset_name = 'Religious texts'
try:
    dataset = Dataset.query.filter(Dataset.name == dataset_name).one()
except NoResultFound:
    dataset = Dataset(name=dataset_name)
    db.session.add(dataset)
    db.session.commit()

import_dataset(
    dataset=dataset,
    data=samples,
    sample_class=Text,
    content_attribute=content_attribute
)
