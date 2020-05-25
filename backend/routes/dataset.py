from flask_restful import abort

from ..config import app
from ..models import DataSetSchema, Dataset


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


# TODO: this function does not still return the next sample, it must be integrated with aL code!
@app.route('/api/<int:data_set_id>', methods=['GET'])
def get_next_data_sample(data_set_id):
    """
    This function responds to a request for /api/int:data_set_id
    with the next data sample of data set that should get labeled

    :param data_set_id:   ID of data set to find
    :return:            data set matching ID
    """
    # Get the data set requested
    data_set = Dataset.query \
        .filter(Dataset.id == data_set_id)

    # Did we find a dataset?
    if data_set is not None:

        # Serialize the data for the response
        dataset_schema = DataSetSchema()
        return dataset_schema.dump(data_set)

    # Otherwise, nope, didn't find next data sample
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
