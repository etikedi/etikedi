from flask import request
from flask_restful import abort, Resource
from flask_praetorian import auth_required, current_user
from sqlalchemy.exc import IntegrityError

from ..config import db, api, app
from ..models import Sample, Association, SampleSchema, Label, Dataset
from ..active_learning_process import notify_about_new_sample, get_next_sample


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
        label_id = None
        try:
            label_id = request.json['label_id']
        except KeyError:
            abort(400)

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
        except IntegrityError:
            return None, 409

        # Retrieve pipe endpoint for process with corresponding dataset_id and send new label
        dataset = Sample.query.get(sample_id).dataset

        notify_about_new_sample(
            dataset=dataset,
            user_id=user.id,
            sample_id=sample_id,
            label_id=label_id
        )

        next_sample = get_next_sample(dataset, app)
        if not next_sample:
            abort(500)
        next_sample.ensure_string_content()
        return SampleSchema().dump(next_sample), 201

    def can_assign(self, sample_id, label_id):
        return bool(db.session.query(Dataset, Sample, Label)
                    .filter(Dataset.id == Sample.dataset_id)
                    .filter(Dataset.id == Label.dataset_id)
                    .filter(Sample.id == sample_id)
                    .filter(Label.id == label_id)
                    .count())


api.add_resource(SampleAPI, '/api/sample/<int:sample_id>')
