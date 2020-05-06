from flask_restful import Resource
from models import db


class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sepal_length = db.Column(db.Float)
    sepal_width = db.Column(db.Float)
    petal_length = db.Column(db.Float)
    petal_width = db.Column(db.Float)
    label = db.Column(db.String, nullable=True)

class FlowersApi(Resource):

    def get(self):
        # Check table in database for new data points
        # result = [SELECT id FROM label_queue WHERE label is Null]
        result = {}
        return result


class FlowerApi(Resource):

    def get(self, id):
        # Get all data to display in frontend
        # result = SELECT * from flowers WHERE id = id;
        result = {}
        return result

    def post(self, id, label):
        # update db and update aL
        # UPDATE label_queue SET label = label WHERE id = id;
        pass
