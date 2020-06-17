""" Preprocessing steps for the DWTC dataset """
import csv
from pathlib import Path
from zipfile import ZipFile

from scipy.io.arff import loadarff

from .generic import import_dataset
from .utils import get_or_create_dataset
from ..config import app
from ..models import Table


def convert_dwtc(data_path: Path):
    dwtc_path = data_path / 'dwtc'

    arff_path = dwtc_path / 'data.arff'
    db_csv_dump_path = dwtc_path / 'table.csv'
    target_csv_path = dwtc_path / 'dwtc.csv'
    target_zip_path = dwtc_path / 'dwtc.zip'

    with arff_path.open() as arff_file, target_csv_path.open('w') as csv_file:
        app.logger.info('Converting DWTC features')
        csv_writer = csv.writer(csv_file)
        data, metadata = loadarff(arff_file)

        feature_names = list(data.dtype.names)
        feature_names[-1] = 'LABEL'
        csv_writer.writerow(feature_names)

        for entry in data:
            entry = list(entry)
            entry[0] = int(entry[0])
            csv_writer.writerow(entry)

    with db_csv_dump_path.open() as table_file, ZipFile(target_zip_path, 'w') as zip_file:
        app.logger.info('Converting DWTC data')
        for entry in list(csv.reader(table_file)):
            identifier, content = entry[0], entry[8]
            zip_file.writestr(f'{identifier}.raw', content)

    import_dataset(
        dataset=get_or_create_dataset('CIFAR'),
        sample_class=Table,
        feature_path=target_csv_path,
        content_path=target_zip_path
    )
