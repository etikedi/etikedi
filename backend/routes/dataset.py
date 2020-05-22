from models.dataset import DataSetSchema, Dataset
import flask
from flask import request
from flask_praetorian import auth_required
from flask_restful import abort

from models import Association, Dataset
from models.datatypes.sample import SampleSchema, Sample
from ..config import app, db


@app.route('/api/datasets', methods=['GET'])
def read_all_data_sets():
    """
    This function responds to a request for /api/datasets
    with the complete lists of data sets

    :return:        json string of list of data sets (e.g. dwtc, religious_texts...)
    """
    # Create the list of data sets from our data
    data_sets = Dataset.query.all()

    # Serialize the data for the response
    data_sets_schema = DataSetSchema(many=True)
    data_set_list = data_sets_schema.dump(data_sets)
    return dict(datasets=data_set_list)


# To do later ->
@app.route('/api/int:data_set_id', methods=['GET'])
def get_next_data_sample(data_set_id):
    """
    This function responds to a request for /api/int:data_set_id
    with the next data sample of data set that should get labeled

    :param data_set_id:   ID of data set to find
    :return:            data set matching ID
    """
    # Get the data set requested
    data_set = Dataset.query \
        .filter(Dataset.dataset_id == data_set_id)

    # Did we find a dataset?
    if data_set is not None:

        # Serialize the data for the response
        person_schema = DataSetSchema()
        return person_schema.dump(data_set)

    # Otherwise, nope, didn't find next data sample
    else:
        abort(404, 'Person not found for Id: {dataset_id}'.format(dataset_id=data_set_id))


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
