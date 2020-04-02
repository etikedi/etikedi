import ast
import csv
import json
import sqlite3
from sqlite3 import Error
from flask import Flask
from models import db
from models.resumees import Resumees

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///testdb.db"

with app.app_context():
    db.init_app(app)
    db.create_all()

    # source: https://dataturks.com/projects/abhishek.narayanan/Entity%20Recognition%20in%20Resumes
    def import_data_turks():
        with open(
            "../../resumee-dataset-creator/datasets/Entity Recognition in Resumes.json"
        ) as f:
            for line in f:
                data = json.loads(line)
                resumee = Resumees(content=data["content"])
                db.session.add(resumee)

        db.session.commit()

    # source: https://www.kaggle.com/maitrip/resumes/data
    def import_kaggle_one():
        with open(
            "../../resumee-dataset-creator/datasets/resumes.csv", "r", encoding="utf-8"
        ) as f:
            csvReader = csv.DictReader(f)
            for line in csvReader:
                try:
                    content = ast.literal_eval(line["Resume"]).decode()
                except SyntaxError:
                    print("Not parsable Resumees String found:")
                    print(line["Resume"])
                    continue
                resumee = Resumees(content=content)
                db.session.add(resumee)
        db.session.commit()

    # source: https://www.kaggle.com/dhainjeamita/resumedataset
    def import_kaggle_two():
        with open("../../resumee-dataset-creator/datasets/resume_dataset.csv") as f:
            csvReader = csv.DictReader(f)
            for line in csvReader:
                resumee = Resumees(content=line["Resume"])
                db.session.add(resumee)
        db.session.commit()

    import_data_turks()
    import_kaggle_one()
    import_kaggle_two()
