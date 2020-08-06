from ..config import db


class User(db.Model):
    """
    Simple user model.

    Taken from the [basic example](https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py) of
    [flask-praetorian](https://github.com/dusktreader/flask-praetorian/).
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(255))
    roles = db.Column(db.Text)
    password = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True, server_default="true")

    def __str__(self):
        return 'User "{}" with roles {}'.format(self.username, self.roles)

    # The following methods are required by flask_praetorian
    def is_valid(self):
        return self.is_active

    @property
    def rolenames(self):
        try:
            return self.roles.split(",")
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id
