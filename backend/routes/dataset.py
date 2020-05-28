from flask_praetorian import auth_required
from flask_restful import abort, Resource

from ..config import app, api
from ..models import DataSetSchema, Dataset


class DatasetList(Resource):
    method_decorators = [auth_required]

    def get(self):
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

    def post(self):
        """ TODO: Create a new dataset """
        pass


class DatasetDetail(Resource):
    method_decorators = [auth_required]

    # TODO: this function does not still return the next sample, it must be integrated with aL code!
    def get(self, dataset_id):
        """
        This function responds to a request for /api/int:data_set_id
        with the next data sample of data set that should get labeled

        :param dataset_id:   ID of data set to find
        :return:            data set matching ID
        """
        # Get the data set requested
        data_set = Dataset.query.filter_by(id=dataset_id).first()

        # Did we find a dataset?
        if data_set is not None:

            # Serialize the data for the response
            dataset_schema = DataSetSchema()
            data_dmp = dataset_schema.dump(data_set)
            print("a")
            return data_dmp
        # Otherwise, nope, didn't find next data sample
        else:
            abort(404)

    def post(self):
        """ TODO: Update name of dataset. """
        pass


api.add_resource(DatasetList, '/api/datasets')
api.add_resource(DatasetDetail, '/api/<int:data_set_id>')


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
