""" Preprocessing steps for the DWTC dataset """
import gzip
import json
from pathlib import Path

import requests

from .generic import import_dataset
from .utils import get_or_create_dataset
from ..config import app
from ..models import Table, Sample

DWTC_URL = 'http://wwwdb.inf.tu-dresden.de/misc/dwtc/data_feb15/dwtc-000.json.gz'


def download_dwtc(data_path: Path):
    if (data_path / 'dwtc-000.json').exists():
        return

    app.logger.info('Downloading DWTC...')
    response = requests.get(DWTC_URL)
    with (data_path / 'dwtc-000.json').open('wb') as f:
        f.write(gzip.decompress(response.content))

    app.logger.info('Download complete')


def import_dwtc(data_path: Path):
    dwtc = get_or_create_dataset(name='DWTC')
    if Sample.query.filter(Sample.dataset == dwtc).count():
        return

    download_dwtc(data_path)

    with (data_path / 'dwtc-000.json').open() as dataset_file:
        lines = dataset_file.readlines()
        raw_json = '[' + ','.join(lines) + ']'
        data = json.loads(raw_json)

    import_dataset(
        dataset=dwtc,
        data=data,
        sample_class=Table,
        content_attribute='relation'
    )
