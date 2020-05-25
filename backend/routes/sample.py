import flask
from flask_restful import abort
from flask_praetorian import auth_required
from ..config import app, db
from ..models import Sample, SampleSchema
from ..models import Association

@app.route('/test', methods=['GET'])
def test():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.

    .. example::
       $ curl http://localhost:5000/login -X POST \
         -d '{"username":"Walter","password":"calmerthanyouare"}'
    """
    return flask.jsonify('hello world'), 200


@app.route('/protected', methods=['GET'])
@auth_required
def protected():
    return flask.jsonify('you should only see this if you are logged in'), 200


@app.route('/api/sample/<int:data_sample_id>', methods=['GET', 'POST'])
def get_sample(data_sample_id):
    """
    This function responds to a request for /api/sample/int:data_set_id
    with the next data sample of data set that should get labeled

    :param data_sample_id:   ID of data sample to find
    :return:            data set matching ID
    """
    if flask.request.method == 'GET':

        sample_obj = Sample.query.filter_by(id=data_sample_id).first()
        if sample_obj is not None:
            return dict(sample=dict(id=sample_obj.id, content=sample_obj.content))
        else:
            abort(404)

    if flask.request.method == 'POST':
        if not flask.request.is_json or flask.request.json.get('association') is None:
            abort(400)
        association_dict = flask.request.json['association']

        # check if label_id and user_id are inside dict
        if not association_dict.keys() >= {'label_id', 'user_id'}:
            abort(400)

        # Query object type referred by ID
        # TODO: check the existence of label_id, user_id
        obj_type = Sample.query.filter_by(id=data_sample_id).first().type

        new_association = Association(sample_id=data_sample_id,
                                      label_id=association_dict['label_id'],
                                      user_id=association_dict['user_id'])
        db.session.add(new_association)
        db.session.commit()

        return ("place next sample here")


