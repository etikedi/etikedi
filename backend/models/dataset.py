from ..aergia import db
from marshmallow_sqlalchemy import ModelSchema

class Dataset(db.Model):
    """
    Represents a complete data set.

    - Name
    - All items
    - Possible features
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)

    def __repr__(self):
        return 'Dataset "{}" ({})'.format(self.name, self.id)

    def __str__(self):
        return self.name


class DataSetSchema(ModelSchema):
    class Meta:
        model = Dataset
        sqla_session = db.session
