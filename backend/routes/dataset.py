from flask_praetorian import auth_required
from flask_restful import abort, Resource

from ..config import app, api
from ..models import DatasetSchema, Dataset


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

    # TODO: this function does not still return the next sample, it must be integrated with aL code!
    def get(self, dataset_id):
        """
        This function responds to a request for /api/int:dataset_id
        with the next data sample of data set that should get labeled

        :param dataset_id:   ID of data set to find
        :return:            data set matching ID
        """
        # Get the dataset requested
        dataset = Dataset.query.filter_by(id=dataset_id).first()

        if dataset is None:
            abort(404)

        return DatasetSchema().dump(dataset)

    def post(self):
        """ TODO: Update name of dataset. """
        pass


api.add_resource(DatasetList, '/api/datasets/')
api.add_resource(DatasetDetail, '/api/datasets/<int:dataset_id>/')


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
