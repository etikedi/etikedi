from ..config import db, ma


class Association(db.Model):
    """ The decision of a user to assign a label to a sample. """
    sample_id = db.Column(
        db.Integer,
        db.ForeignKey('sample.id'),
        primary_key=True
    )
    sample = db.relationship(
        'Sample',
        backref='associations'
    )

    label_id = db.Column(
        db.Integer,
        db.ForeignKey('label.id'),
        primary_key=True
    )
    label = db.relationship(
        'Label',
        backref='associations'
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True
    )
    user = db.relationship(
        'User',
        backref='associations'
    )


class AssociationSchema(ma.Schema):
    class Meta:
        fields = ("sample_id", "label_id", "user_id")
