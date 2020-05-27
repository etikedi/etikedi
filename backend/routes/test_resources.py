import random

from flask import request
from flask_restful import Resource

from active_learning_process.process_management import ProcessManager

manager = ProcessManager()


class Index(Resource):

    def get(self):
        sample_ids = []
        backend_endpoint = manager.get_or_else_load("iris")
        print("Backend:\tQuerying process for dataset iris")
        if backend_endpoint.poll(5):
            print("Backend:\tFound new datapoints")
            sample_ids = backend_endpoint.recv()
        else:
            print("Backend:\tNo samples available atm")
        return sample_ids


class New(Resource):

    def get(self):
        id = request.args.get("sample", default=0, type=int)
        label = random.randint(0, 2)
        backend_endoint = manager.get_or_else_load("iris")
        data = {"id": id, "label": label, "user": 1}
        backend_endoint.send(data)
        return data
