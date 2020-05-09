import ast
import csv
import json
import sqlite3
from pprint import pprint
from sqlite3 import Error
from flask import Flask
from sklearn import datasets

from backend.models import db
from backend.models.label_queue import Flower

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///testdb.db"

with app.app_context():
    db.init_app(app)
    db.create_all()
    iris = datasets.load_iris()
    labels = iris.target
    data = iris.data
    sepal_lengths = data[:, :1]
    sepal_widths = data[:, 1:2]
    petal_lengts = data[:, 2:3]
    petal_widths = data[:, 3:4]
    for i in range(0, len(data)):
        id = i
        sepal_length = sepal_lengths.item(i)
        sepal_width = sepal_widths.item(i)
        petal_length = petal_lengts.item(i)
        petal_width = petal_widths.item(i)
        label = labels[i]
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
    #
    # # source: https://dataturks.com/projects/abhishek.narayanan/Entity%20Recognition%20in%20Resumes
    # def import_data_turks():
    #     with open(
    #         "../../resumee-dataset-creator/datasets/Entity Recognition in Resumes.json"
    #     ) as f:
    #         for line in f:
    #             data = json.loads(line)
    #             resumee = Resumees(content=data["content"])
    #             db.session.add(resumee)
    #
    #     db.session.commit()
    #
    # # source: https://www.kaggle.com/maitrip/resumes/data
    # def import_kaggle_one():
    #     with open(
    #         "../../resumee-dataset-creator/datasets/resumes.csv", "r", encoding="utf-8"
    #     ) as f:
    #         csvReader = csv.DictReader(f)
    #         for line in csvReader:
    #             try:
    #                 content = ast.literal_eval(line["Resume"]).decode()
    #             except SyntaxError:
    #                 print("Not parsable Resumees String found:")
    #                 print(line["Resume"])
    #                 continue
    #             resumee = Resumees(content=content)
    #             db.session.add(resumee)
    #     db.session.commit()
    #
    # # source: https://www.kaggle.com/dhainjeamita/resumedataset
    # def import_kaggle_two():
    #     with open("../../resumee-dataset-creator/datasets/resume_dataset.csv") as f:
    #         csvReader = csv.DictReader(f)
    #         for line in csvReader:
    #             resumee = Resumees(content=line["Resume"])
    #             db.session.add(resumee)
    #     db.session.commit()
    #
    # import_data_turks()
    # import_kaggle_one()
    # import_kaggle_two()
