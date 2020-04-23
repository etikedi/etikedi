from .sample import Sample
from ...aergia import db


class Text(Sample):
    """ Represents some raw text. """
    __tablename__ = 'text'

    id = db.Column(db.Integer, db.ForeignKey('sample.id'), primary_key=True)
    content = db.Column(db.Text())

    __mapper_args__ = {
        'polymorphic_identity': 'text'
    }
