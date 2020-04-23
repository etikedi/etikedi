from .sample import Sample
from ...aergia import db


class Table(Sample):
    __tablename__ = 'table'

    id = db.Column(db.Integer, db.ForeignKey('sample.id'), primary_key=True)
    content = db.Column(db.Text())

    __mapper_args__ = {
        'polymorphic_identity': 'table'
    }
