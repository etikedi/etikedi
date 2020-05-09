from flask import Flask, make_response, abort
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from models.dataset import DataSetSchema, Dataset
from models.label import LabelSchema
from .config import Config
from models import dataset, Label

app = Flask(__name__)
app.config.from_object(Config())

# Make the creation of REST endpoints a lot easier
api = Api(app)

# Configure Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create the database handler
db = SQLAlchemy(app)

with app.app_context():
    db.init_app(app)
    db.create_all()

# Initialize Marshmallow
ma = Marshmallow(app)


@app.route('/api/<data_sets>', methods=['GET'])
def read_all_data_sets(data_sets):
    """
    This function responds to a request for /api/data_sets
    with the complete lists of data sets

    :return:        json string of list of data sets (e.g. dwtc, religios texts...)
    """
    # Create the list of data sets from our data
    data_sets = Dataset.query \
        .order_by(Dataset.lname) \
        .all()

    # Serialize the data for the response
    data_sets_schema = DataSetSchema(many=True)
    return data_sets_schema.dump(data_sets).data


@app.route('/api/<data_set_id>', methods=['GET'])
def read_one(data_set_id):
    """
    This function responds to a request for /api/{dataset_id}
    with one matching person from people

    :param data_set_id:   ID of data set to find
    :return:            data set matching ID
    """
    # Get the data set requested
    data_set = Dataset.query \
        .filter(Dataset.dataset_id == data_set_id) \
        .one_or_none()

    # Did we find a dataset?
    if dataset is not None:

        # Serialize the data for the response
        person_schema = DataSetSchema()
        return person_schema.dump(dataset).data

    # Otherwise, nope, didn't find that person
    else:
        abort(404, 'Person not found for Id: {dataset_id}'.format(dataset_id=dataset_id))


@app.route('/api/{data_set_id}/labels', methodes=['GET'])
def read_all_labels():
    """
    This function responds to a request for /api/{dataset_id}/labels
    with the complete lists of data sets

    :return:        json string of list of labels for a data set
    """
    # Create the list of labels of this data set
    labels = Label.query \
        .order_by(Label.lname) \
        .all()

    # Serialize the data for the response
    label_schema = LabelSchema(many=True)
    return label_schema.dump(labels).data


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
