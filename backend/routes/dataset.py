from flask_praetorian import auth_required
from flask_restful import abort, Resource
from sqlalchemy import func as db_functions

from ..config import app, api
from ..models import DatasetSchema, Dataset, Association, Sample
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


def should_label_random_sample(dataset: Dataset, random_sample_every: int = 10) -> bool:
    number_of_labeled_samples = Association.query.join(Association.sample).filter(Sample.dataset == dataset).count()
    return number_of_labeled_samples % random_sample_every


def get_random_unlabelled_sample(dataset: Dataset) -> Sample:
    return Sample.query.filter(
        Sample.dataset == dataset,
        ~Sample.associations.any()
    ).order_by(db_functions.random()).first()


class DatasetDetail(Resource):
    method_decorators = [auth_required]

    def get(self, dataset_id):
        """
        This function responds to a request for /api/int:dataset_id
        with the next data sample of data set that should get labeled

        :param dataset_id:   ID of data set to find
        :return:            data set matching ID
        """
        dataset = Dataset.query.filter_by(id=dataset_id).first()

        if dataset is None:
            abort(404)

        if should_label_random_sample(dataset=dataset):
            return get_random_unlabelled_sample(dataset).id, 200

        # Retrieve pipe endpoint from process manager
        process_resources = manager.get_or_else_load(dataset_id)
        pipe_endpoint = process_resources["pipe"]

        if pipe_endpoint.poll(5):
            app.logger.info("Found new datapoints")
            next_sample_id = pipe_endpoint.recv()
            return next_sample_id
        else:
            # Send back a random label anyway for testing purposes
            app.logger.info("No samples available from AL, send back a random sample instead")
            return get_random_unlabelled_sample(dataset).id, 200

    def post(self):
        """ TODO: Update name of dataset. """
        pass


api.add_resource(DatasetList, '/api/datasets/')
api.add_resource(DatasetDetail, '/api/datasets/<int:dataset_id>/')


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
