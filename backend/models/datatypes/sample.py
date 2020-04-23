from sqlalchemy import ForeignKey
from ...aergia import db


class Sample(db.Model):
    """ A generic data item. """
    __tablename__ = 'sample'

    id = db.Column(db.Integer, primary_key=True)

    features = db.Column(db.Text(), nullable=True)

    dataset_id = db.Column(db.Integer, ForeignKey('dataset.id'), nullable=False)
    dataset = db.relationship(
        'Dataset',
        backref=db.backref('items', lazy=True)
    )

    labels = db.relationship(
        'Label',
        secondary='association',
        lazy='subquery',
        # TODO: Figure out the difference to `back_populates`
        backref=db.backref('samples', lazy=True)
    )

    # Saves concrete type of data in this sample
    type = db.Column(db.VARCHAR(10))

    __mapper_args__ = {
        'polymorphic_identity':'employee',
        'polymorphic_on': 'type'
    }