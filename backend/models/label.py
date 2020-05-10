from sqlalchemy import ForeignKey
from marshmallow_sqlalchemy import ModelSchema
from ..aergia import db, ma


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


class LabelSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Label
        sqla_session = db.session

