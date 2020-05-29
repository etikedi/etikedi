from flask import request, jsonify
from flask_restful import abort, Resource
from flask_praetorian import auth_required, current_user
from sqlalchemy.exc import IntegrityError

from ..config import db, api
from ..models import Sample, Association, SampleSchema, Label, Dataset
from ..active_learning_process.process_management import manager


class SampleAPI(Resource):
    method_decorators = [auth_required]

    def get(self, sample_id):
        sample = Sample.query.filter_by(id=sample_id).first()
        if sample is None:
            abort(404)

        return SampleSchema().dump(sample)

    def post(self, sample_id):
        """
        This function responds to a request for /api/sample/int:data_sample_id
        with the next data sample of data set that should get labeled

        :param sample_id:   ID of data sample to find
        :return:            data set matching ID
        """
        user = current_user()
        try:
            label_id = request.json['label_id']
        except KeyError:
            abort(400)
            return

        if not self.can_assign(sample_id, label_id):
            abort(400)

        try:
            new_association = Association(
                sample_id=sample_id,
                label_id=label_id,
                user_id=user.id
            )
            db.session.add(new_association)
            db.session.commit()

            # Retrieve pipe endpoint for process with corresponding dataset_id and send new label
            dataset_id = Sample.query.get(sample_id).dataset_id
            process_resources = manager.get_or_else_load(dataset_id)
            pipe_endpoint = process_resources["pipe"]
            pipe_endpoint.send({"id": new_association.sample_id,
                                "label": new_association.label_id,
                                "user": new_association.user_id})

            # Check for new sample and return. Return None, 409 otherwise
            if pipe_endpoint.poll(5):
                print("Backend:\tFound new datapoints")
                next_sample_id = pipe_endpoint.recv()
                next_sample = Sample.query.get(next_sample_id)
                return SampleSchema().dump(next_sample), 201
            else:
                print("Backend:\tNo samples available atm")
                return None, 409
        except IntegrityError:
            return None, 409

    def can_assign(self, sample_id, label_id):
        return bool(db.session.query(Dataset, Sample, Label)
                    .filter(Dataset.id == Sample.dataset_id)
                    .filter(Dataset.id == Label.dataset_id)
                    .filter(Sample.id == sample_id)
                    .filter(Label.id == label_id)
                    .count())


api.add_resource(SampleAPI, '/api/sample/<int:sample_id>')
