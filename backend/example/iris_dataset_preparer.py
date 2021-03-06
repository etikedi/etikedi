# import numpy as np
# from sklearn import datasets
#
# from .config import app, db
# from .models.iris_model import Flower
#
# with app.app_context():
#     db.init_app(app)
#     db.create_all()
#     iris = datasets.load_iris()
#     labels = iris.target
#     data = iris.data
#     sepal_lengths = data[:, :1]
#     sepal_widths = data[:, 1:2]
#     petal_lengths = data[:, 2:3]
#     petal_widths = data[:, 3:4]
#     for i in range(0, len(data)):
#         id = i
#         sepal_length = sepal_lengths.item(i)
#         sepal_width = sepal_widths.item(i)
#         petal_length = petal_lengths.item(i)
#         petal_width = petal_widths.item(i)
#         label = np.take(labels, i).item()
#         flower = Flower(
#             id=id,
#             sepal_length=sepal_length,
#             sepal_width=sepal_width,
#             petal_length=petal_length,
#             petal_width=petal_width,
#             label=label,
#         )
#         db.add(flower)
#     db.commit()
#     print("done")
