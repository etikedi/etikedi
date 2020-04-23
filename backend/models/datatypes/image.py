from .sample import Sample
from ...aergia import db


class Image(Sample):
    """ Stores the binary data of an image. """
    __tablename__ = 'image'

    id = db.Column(db.Integer, db.ForeignKey('sample.id'), primary_key=True)
    data = db.Column(db.BLOB)

    __mapper_args__ = {
        'polymorphic_identity': 'image'
    }
