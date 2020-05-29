import random

from flask import request
from flask_restful import Resource

from backend.config import api
from backend.active_learning_process.process_management import manager


class Index(Resource):

    def get(self):
        sample_id = []
        process_resources = manager.get_or_else_load("iris")
        print("Backend:\tQuerying process for dataset iris")
        if process_resources["pipe"].poll(5):
            print("Backend:\tFound new datapoints")
            sample_id = process_resources["pipe"].recv()
        else:
            print("Backend:\tNo samples available atm")
        return sample_id


class New(Resource):

    def get(self):
        id = request.args.get("sample", default=0, type=int)
        label = random.randint(0, 2)
        process_resources = manager.get_or_else_load("iris")
        data = {"id": id, "label": label, "user": 1}
        process_resources["pipe"].send(data)
        return data


api.add_resource(Index, "/api/index")
api.add_resource(New, "/api/new")
