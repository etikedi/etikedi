import flask
from flask_restful import abort, Resource
from flask_praetorian import auth_required
from ..config import db, api
from ..models import Sample, Association


class SampleAPI(Resource):
    method_decorators = [auth_required]

    def get(self, data_sample_id):
        sample_obj = Sample.query.filter_by(id=data_sample_id).first()
        if sample_obj is None:
            abort(404)
        return dict(sample=dict(id=sample_obj.id, content=sample_obj.content))

    def post(self, data_sample_id):
        """
        This function responds to a request for /api/sample/int:data_set_id
        with the next data sample of data set that should get labeled

        :param data_sample_id:   ID of data sample to find
        :return:            data set matching ID
        """
        if not flask.request.is_json or flask.request.json.get('association') is None:
            abort(400)
        association_dict = flask.request.json['association']

        # check if label_id and user_id are inside dict
        if not association_dict.keys() >= {'label_id', 'user_id'}:
            abort(400)

        # Query object type referred by ID
        # TODO: check the existence of label_id, user_id
        obj_type = Sample.query.filter_by(id=data_sample_id).first().type

        new_association = Association(
            sample_id=data_sample_id,
            label_id=association_dict['label_id'],
            user_id=association_dict['user_id']
        )
        db.session.add(new_association)
        db.session.commit()

        return ("you just posted into /api/sample/<id>, aL code integration is still a TODO!")


api.add_resource(SampleAPI, '/api/sample/<int:data_sample_id>')
