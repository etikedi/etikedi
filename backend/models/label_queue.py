from flask_restful import Resource
from ..aergia import db


class LabelQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
