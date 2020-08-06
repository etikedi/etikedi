import dataclasses
import json

from flask import request
from flask_praetorian import auth_required
from flask_restful import Resource
from marshmallow import ValidationError

from ..active_learning_process.process_management import manager
from ..config import api, db, ALConfigSchema
from ..models import Dataset


class ConfigAPI(Resource):
    method_decorators = [auth_required]

    def get(self, dataset_id):
        """ Return the current configuration for the given dataset. """
        dataset = Dataset.query.get(dataset_id)

        if not dataset:
            return None, 404

        return json.loads(dataset.config), 200

    def post(self, dataset_id):
        """ Update the configuration for the given dataset. Implies a restart of the AL process. """
        dataset = Dataset.query.get(dataset_id)

        if not dataset:
            return None, 404

        try:
            new_config = ALConfigSchema().load(
                {k.upper(): v for k, v in request.form.items()}
            )
        except ValidationError as e:
            return e.messages, 400

        dataset.config = json.dumps(dataclasses.asdict(new_config))
        db.session.commit()

        manager.restart_with_config(dataset, json.loads(dataset.config))

        return None, 204


api.add_resource(ConfigAPI, "/api/datasets/<int:dataset_id>/config")
