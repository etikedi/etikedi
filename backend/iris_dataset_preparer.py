from pprint import pprint

from sklearn import datasets
import numpy as np
from backend.models.label_queue import Flower
from config import app, db

with app.app_context():
    db.init_app(app)
    db.create_all()
    iris = datasets.load_iris()
    labels = iris.target
    data = iris.data
    sepal_lengths = data[:, :1]
    sepal_widths = data[:, 1:2]
    petal_lengths = data[:, 2:3]
    petal_widths = data[:, 3:4]
    for i in range(0, len(data)):
        id = i
        sepal_length = sepal_lengths.item(i)
        sepal_width = sepal_widths.item(i)
        petal_length = petal_lengths.item(i)
        petal_width = petal_widths.item(i)
        label = np.take(labels, i).item()
        print(type(label))
        pprint(id)
        pprint(sepal_length)
        pprint(sepal_width)
        pprint(petal_length)
        pprint(petal_width)
        pprint(label)
        flower = Flower(id=id, sepal_length=sepal_length, sepal_width=sepal_width, petal_length=petal_length,
                        petal_width=petal_width, label=label)
        db.session.add(flower)
    db.session.commit()
    print("done")
