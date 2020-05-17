from ..aergia import db


class User(db.Model):
    """
    Simple user model.

    To be extended with role based permissions. Maybe replaced by a model
    from a third-party library like Flask-Login.
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.VARCHAR(255))
    last_name = db.Column(db.VARCHAR(255))
    email = db.Column(db.VARCHAR(255))