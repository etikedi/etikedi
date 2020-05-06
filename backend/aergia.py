import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from models import db
from models.flowers import FlowersApi, FlowerApi

app = Flask(__name__)
app.config.from_object("config.Config")
api = Api(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

with app.app_context():
    db.init_app(app)
    db.create_all()

    api.add_resource(FlowersApi, "/api/flowers")
    api.add_resource(FlowerApi, "/api/flowers/")

@app.route("/api/index")
def get():
    # p = ActiveLearningProcess()
    # p.start()
    os.system("active_learning_process.py")

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    return app

if __name__ == "__main__":
    app.run()
