from flask_praetorian import auth_required
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from .utils import convert_dataclass_to_parser
from ..config import api
from ..models import Dataset
from ..active_learning_process.al_config import config, ALConfig


config_parser = convert_dataclass_to_parser(ALConfig)


class ConfigAPI(Resource):
    method_decorators = [auth_required]

    def get(self, dataset_id):
        """
        Return the current configuration for the given dataset.

        TODO: When AL merged, store one saved configuration per dataset in database.
        """
        dataset = Dataset.query.get(dataset_id)

        if not dataset:
            return None, 404

        return config.__dict__

    def post(self, dataset_id):
        """ Update the configuration for the given dataset. Implies a restart of the AL process. """
        dataset = Dataset.query.get(dataset_id)

        if not dataset:
            return None, 404

        try:
            args = config_parser.parse_args()
        except BadRequest as e:
            e.data = e.data['message']  # Prevent nesting the error messages more than actually needed
            raise e
        return None, 204


api.add_resource(ConfigAPI, '/api/datasets/<int:dataset_id>/config')