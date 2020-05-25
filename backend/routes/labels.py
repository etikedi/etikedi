from flask_restful import abort

from ..config import app
from ..models import Label, LabelSchema


@app.route('/api/int:data_set_id/labels', methods=['GET'])
def read_all_labels(data_set_id):
    """
    This function responds to a request for /api/int:data_set_id/labels
    with the complete lists of data sets

    :return:        json string of list of labels for a data set
    """
    # Create the list of labels of this data set
    labels = Label.query.filter(Label.dataset_id == data_set_id)

    # Did we find a label?
    if labels is not None:

        # Serialize the data for the response
        label_schema = LabelSchema(many=True)
        label_list = label_schema.dump(labels)
        return dict(labels=label_list)

        # Otherwise, nope, didn't find labels
    else:
        abort(404, 'Labels not found for data set: {dataset_id}'.format(dataset_id=data_set_id))


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
