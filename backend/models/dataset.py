from ..config import db, ma


class Dataset(db.Model):
    """
    Represents a complete dataset.

    - Name
    - All items
    - Possible features
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    # feature_names = db.Column(db.ARRAY(db.String()))

    def __repr__(self):
        return 'Dataset "{}" ({})'.format(self.name, self.id)

    def __str__(self):
        return self.name


class DatasetSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")
