from ..aergia import db


class Dataset(db.Model):
    """
    Represents a complete dataset.

    - Name
    - All items
    - Possible features
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
