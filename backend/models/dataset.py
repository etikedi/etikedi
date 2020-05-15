from app_init import db


class Dataset(db.Model):
    """
    Represents a complete dataset.

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
