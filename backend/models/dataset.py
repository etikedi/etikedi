import json
import dataclasses
from ..config import db, ma, default_al_config


class Dataset(db.Model):
    """ Represents a complete dataset. """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    feature_names = db.Column(db.String(), nullable=True)
    features = db.Column(db.Text(), nullable=True)
    config = db.Column(
        db.Text(),
        nullable=True,
        default=json.dumps(dataclasses.asdict(default_al_config)),
    )

    def __repr__(self):
        return 'Dataset "{}" ({})'.format(self.name, self.id)

    def __str__(self):
        return self.name


class DatasetSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")
