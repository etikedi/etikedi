import flask
from flask_praetorian import auth_required

from ..config import app


@app.route('/test', methods=['get'])
def test():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.

    .. example::
       $ curl http://localhost:5000/login -X POST \
         -d '{"username":"Walter","password":"calmerthanyouare"}'
    """
    return flask.jsonify('hello world'), 200


@app.route('/protected', methods=['get'])
@auth_required
def protected():
    return flask.jsonify('you should only see this if you are logged in'), 200
