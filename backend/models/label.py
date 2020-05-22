from sqlalchemy import ForeignKey

from config import db


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    dataset_id = db.Column(
        db.Integer,
        ForeignKey('dataset.id'),
        nullable=False
    )
    dataset = db.relationship(
        'Dataset',
        backref=db.backref('labels', lazy=True)
    )

