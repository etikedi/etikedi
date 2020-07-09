import base64
from typing import Union
from sqlalchemy import ForeignKey
from ...config import db, ma


class Sample(db.Model):
    """
    Base class for samples.

    Uses joined table inheritance to enable polymorphic fetching of
    concrete samples of a specific data table. Documentation about how
    this works can be found in the [docs](https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/inheritance.html)
    """
    __tablename__ = 'sample'

    id = db.Column(db.Integer, primary_key=True)

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

    content: Union[str, bytes]

    __mapper_args__ = {
        'polymorphic_identity': 'sample',
        'polymorphic_on': 'type'
    }

    def ensure_string_content(self) -> None:
        """ Converts the content to a base64 encoded string if it is binary """
        self.content = base64.b64encode(self.content).decode()

    def __str__(self):
        return 'Sample {} in {}'.format(self.id, self.dataset)

    def __repr__(self):
        return str(self)


class SampleSchema(ma.Schema):
    class Meta:
        fields = ("id", "dataset_id", "type", "content")
