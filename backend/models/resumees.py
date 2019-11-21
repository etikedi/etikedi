from models import db
from flask_restful import reqparse, Resource
from sqlalchemy.orm import class_mapper
import sqlalchemy

from datetime import datetime


class Resumees(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), unique=False, nullable=False)
    label = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ResumeesApi(Resource):
    def get(self, resumeeId):
        return Resumees.query.get(resumeeId).as_dict()


class ResumeesListApi(Resource):
    def get(self):
        resumees = []
        for r in Resumees.query.all():
            #  p
            #  resumee = _prepare_dict_for_json(r.__dict__)
            resumees.append(r.as_dict())
        return resumees
