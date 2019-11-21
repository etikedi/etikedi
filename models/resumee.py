from models import db


class Resumee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), unique=False, nullable=False)
    label = db.Column(db.Integer)
