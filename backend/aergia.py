from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from models import db
from models.resumees import ResumeesApi, ResumeesListApi

app = Flask(__name__)
app.config.from_object("config.Config")
api = Api(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

with app.app_context():
    db.init_app(app)
    db.create_all()

    api.add_resource(ResumeesApi, "/api/resumees/<resumeeId>")
    api.add_resource(ResumeesListApi, "/api/resumees")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
