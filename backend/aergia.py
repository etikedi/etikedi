from flask import Flask, make_response, abort, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from .config import Config

app = Flask(__name__)
app.config.from_object(Config())

# Make the creation of REST endpoints a lot easier
api = Api(app)

# Configure Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create the database handler
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

from .models.dataset import DataSetSchema
from .models.label import LabelSchema
from .models.datatypes.sample import SampleSchema
from .models.association import AssociationSchema
from .models import Label, Sample, Dataset, Association

with app.app_context():
    db.init_app(app)
    db.create_all()


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
@app.route('/api/<int:data_set_id>', methods=['GET'])
def get_next_data_sample(data_set_id):
    """
    This function responds to a request for /api/<int:data_set_id>
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


@app.route('/api/<int:data_set_id>/labels', methods=['GET'])
def read_all_labels(data_set_id):
    """
    This function responds to a request for /api/<int:data_set_id>/labels
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


@app.route('/api/sample/<int:datasample_id>', methods=['GET'])
def get_sample_by_id(datasample_id):
    """
    This function responds to a request for /api/sample/<int:datasample_id>
    with one matching data sample

    :param datasample_id:   ID of data sample to find
    :return:            data sample matching ID
    """
    # Get the data sample requested
    data_sample = Sample.query \
        .filter(Sample.id == datasample_id) \
        .one_or_none()

    # Did we find a dataset?
    if data_sample is not None:

        # Serialize the data for the response
        data_sample_schema = SampleSchema()
        data_sample_list = data_sample_schema.dump(data_sample)
        return dict(data_sample=data_sample_list)

    # Otherwise, nope, didn't find that data sample
    else:
        abort(404, 'Data sample not found for Id: {datasample_id}'.format(datasample_id=datasample_id))


# to do return next label
@app.route('/api/sample', methods=['POST'])
def label_sample():
    """
        This function adds an association for /api/{dataset_id}

        :param sample_id, label_id, user_id:   ID of data set to find
        :return:            201 on success, 404 if data sample doesn't exist
        """
    sample_id = request.args['sample_id']
    label_id = request.form['label_id']
    user_id = request.form['user_id']

    # Check if the data sample requested exists
    existing_sample = Sample.query \
        .filter(Sample.id == sample_id) \
        .one_or_none()

    if existing_sample is not None:

        # Create a association using the schema and the passed-in datasample_id, label_id, user_id
        new_association = {
            "sample_id": sample_id,
            "label_id": label_id,
            "user_id": user_id,
        }

        # **na = (sample_id=sample
        # Add the association to the database
        db.session.add(Association(**new_association))
        db.session.commit()

        # Serialize and return the newly created association in the response
        return new_association, 201

        # Otherwise, nope, data sample doesn't exist
    else:
        abort(404, f'Data sample {sample_id} doesn`t exist')


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
