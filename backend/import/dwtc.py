""" Preprocessing steps for the DWTC dataset """
import json
from .import_dataset import import_dataset
from ..models import Table, Dataset

PATH = '/Users/nick/Code/Aergia/backend/data/dwtc-000.json'

with open(PATH) as dataset_file:
    lines = dataset_file.readlines()
    raw_json = '[' + ','.join(lines) + ']'
    data = json.loads(raw_json)

import_dataset(
    dataset=Dataset.query.get(1),
    data=data,
    sample_class=Table,
    content_attribute='relation'
)
