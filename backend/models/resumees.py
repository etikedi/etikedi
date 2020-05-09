from flask_restful import Resource

from models import db


class Resumees(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), unique=False, nullable=False)

    #  label = db.Column(db.Integer, default=0)

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        result["features"] = self.generateFeatures()
        return result


class ResumeesApi(Resource):
    def get(self):

        return []


class ResumeesListApi(Resource):
    def post(self, id, label):
        resumees = []
        for r in Resumees.query.all():
            resumees.append(r.as_dict())
        return resumees
