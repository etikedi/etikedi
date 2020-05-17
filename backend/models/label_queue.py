from config import db


class LabelQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sepal_length = db.Column(db.Float)
    sepal_width = db.Column(db.Float)
    petal_length = db.Column(db.Float)
    petal_width = db.Column(db.Float)
    label = db.Column(db.Integer)

