from flask_praetorian import auth_required
from flask_restful import abort, Resource
from sqlalchemy import func as db_functions

from ..config import app, api, db
from ..models import DatasetSchema, Dataset, Association, Label, Sample
from ..active_learning_process.process_management import manager
from ..active_learning_process.al_config import config


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


def dataset_has_one_sample_for_each_label(dataset: Dataset) -> bool:
    """
    Checks if there is at least one sample associated to each label available.

    The check is necessary for the active learning code to start. If the check fails, return a random
    sample instead.
    """
    associated_label_ids = db.session.query(Association.label_id).join(Association.sample).filter(
        Sample.dataset == dataset).distinct().all()
    all_label_ids = {label.id for label in dataset.labels}

    # When querying only a single column, SQLAlchemy still returns tuples (with just one element)
    associated_label_ids = [x[0] for x in associated_label_ids]

    return set(associated_label_ids) == all_label_ids


def should_label_random_sample(dataset: Dataset, random_sample_every: int = 10) -> bool:
    if not dataset_has_one_sample_for_each_label(dataset):
        return True

    number_of_labeled_samples = Association.query.join(Association.sample).filter(Sample.dataset_id == 2).count()
    if number_of_labeled_samples % random_sample_every:
        return True

    return False


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
        # dataset_id = 0 corresponds to iris database for test runs
        if dataset_id > 0:
            dataset = Dataset.query.filter_by(id=dataset_id).first()

            if dataset is None:
                abort(404)

        if should_label_random_sample(dataset, random_sample_every=config().RANDOM_SAMPLE_EVERY):
            random_sample = Sample.query.filter(
                Sample.dataset_id == 2,
                ~Sample.associations.any()
            ).order_by(db_functions.random()).first()

            return random_sample.id, 200

        # Retrieve pipe endpoint from process manager
        process_resources = manager.get_or_else_load(dataset_id)
        pipe_endpoint = process_resources["pipe"]
        # Poll for new data points
        if pipe_endpoint.poll(5):
            app.logger.info("Found new datapoints")
            next_sample_id = pipe_endpoint.recv()
            return next_sample_id
        else:
            # What should happen here? Wait and try again?
            app.logger.info("No samples available at the moment")
            return []

    def post(self):
        """ TODO: Update name of dataset. """
        pass


api.add_resource(DatasetList, '/api/datasets/')
api.add_resource(DatasetDetail, '/api/datasets/<int:dataset_id>/')


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
