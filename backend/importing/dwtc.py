""" Preprocessing steps for the DWTC dataset """
import gzip
import json
import csv
from pathlib import Path

import requests
from scipy.io.arff import loadarff

from .generic import import_dataset
from .utils import get_or_create_dataset
from ..config import app
from ..models import Table, Sample

DWTC_URL = 'http://wwwdb.inf.tu-dresden.de/misc/dwtc/data_feb15/dwtc-000.json.gz'


# def download_dwtc(data_path: Path):
#     if (data_path / 'dwtc-000.json').exists():
#         return
#
#     app.logger.info('Downloading DWTC...')
#     response = requests.get(DWTC_URL)
#     with (data_path / 'dwtc-000.json').open('wb') as f:
#         f.write(gzip.decompress(response.content))
#
#     app.logger.info('Download complete')
#
#
# def import_dwtc(data_path: Path):
#     dwtc = get_or_create_dataset(name='DWTC')
#     if Sample.query.filter(Sample.dataset == dwtc).count():
#         return
#
#     download_dwtc(data_path)
#
#     with (data_path / 'dwtc-000.json').open() as dataset_file:
#         lines = dataset_file.readlines()
#         raw_json = '[' + ','.join(lines) + ']'
#         data = json.loads(raw_json)
#
#     import_dataset(
#         dataset=dwtc,
#         data=data,
#         sample_class=Table,
#         content_attribute='relation'
#     )


def import_dwtc(data_path: Path):
    dwtc_path = data_path / 'dwtc'
    with (dwtc_path / 'data.arff').open() as arff_file:
        arff = loadarff(arff_file)
    with (dwtc_path / 'table.csv').open() as table_file:
        raw_data = list(csv.reader(table_file))
        # A dictionary with the id of the table as the key and the html content as the value
        content = {int(entry[0]): entry[8] for entry in raw_data}

    data, metadata = arff
    feature_names = data.dtype.names
    possible_labels = metadata._attributes['CLASS'].values

