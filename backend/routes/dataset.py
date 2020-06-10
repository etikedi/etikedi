from flask import jsonify
from flask_praetorian import auth_required
from flask_restful import abort, Resource

from ..config import app, api
from ..models import DatasetSchema, Dataset
from ..active_learning_process.process_management import manager


class DatasetList(Resource):
    method_decorators = [auth_required]

    def get(self):
        """
        This function responds to a request for /api/datasets
        with the complete lists of data sets

        :return:        list of datasets (e.g. dwtc, religious_texts...)
        """
        datasets = Dataset.query.all()
        return DatasetSchema(many=True).dump(datasets)

    def post(self):
        """ TODO: Create a new dataset """
        pass


class DatasetDetail(Resource):
    method_decorators = [auth_required]

    def get(self, dataset_id):
        """
        This function responds to a request for /api/int:dataset_id
        with the next data sample of data set that should get labeled

        :param dataset_id:   ID of data set to find
        :return:            data set matching ID
        """
        # Get the dataset requested
        # dataset_id = -1 corresponds to iris database for test runs
        if dataset_id != -1:
            dataset = Dataset.query.filter_by(id=dataset_id).first()

            if dataset is None:
                abort(404)

        # Retrieve pipe endpoint from process manager
        process_resources = manager.get_or_else_load(dataset_id)
        pipe_endpoint = process_resources["pipe"]
        # Poll for new data points
        if pipe_endpoint.poll(5):
            app.logger.info("Backend:\tFound new datapoints")
            next_sample_id = pipe_endpoint.recv()
            return next_sample_id
        else:
            # What should happen here? Wait and try again?
            app.logger.info("Backend:\tNo samples available atm")
            return None

    def post(self):
        """ TODO: Update name of dataset. """
        pass


api.add_resource(DatasetList, '/api/datasets/')
api.add_resource(DatasetDetail, '/api/datasets/<int:dataset_id>/')


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
