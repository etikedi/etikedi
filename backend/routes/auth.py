# import flask
#
# from ..config import app, guard
#
#
# @app.route("/login", methods=["POST"])
# def login():
#     """
#     Logs a user in by parsing a POST request containing user credentials and
#     issuing a JWT token.
#
#     .. example::
#        $ curl http://localhost:5000/login -X POST \
#          -d '{"username":"Walter","password":"calmerthanyouare"}'
#     """
#     req = flask.request.get_json(force=True)
#
#     username = req.get("username", None)
#     password = req.get("password", None)
#
#     user = guard.authenticate(username, password)
#     payload = {"access_token": guard.encode_jwt_token(user)}
#     status_code = 200
#
#     return flask.jsonify(payload), status_code
#
#
# @app.route("/refresh", methods=["GET"])
# def refresh():
#     """
#     Refreshes an existing JWT by creating a new one that is a copy of the old
#     except that it has a refrehsed access expiration.
#     .. example::
#        $ curl http://localhost:5000/refresh -X GET \
#          -H "Authorization: Bearer <your_token>"
#     """
#     old_token = guard.read_token_from_header()
#     new_token = guard.refresh_jwt_token(old_token)
#
#     ret = {"access_token": new_token}
#     return flask.jsonify(ret), 200
