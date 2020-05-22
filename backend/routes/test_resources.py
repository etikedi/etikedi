import random
from multiprocessing import Queue

from flask import request
from flask_restful import Resource

from active_learning_process.al_process import ALProcess

to_label_queue = Queue()
label_queue = Queue()
process_dict = {}


class Start(Resource):
    def get(self):
        aL = ALProcess("iris", to_label_queue, label_queue)
        process_dict["iris"] = (aL, label_queue)
        aL.start()
        return "Started"


class Index(Resource):

    def get(self):
        sample_ids = []
        if not to_label_queue.empty():
            sample_ids = to_label_queue.get()
        else:
            print("No data available")
        return sample_ids
        # queue_entries = to_be_labeled()
        # sample_ids = [entry.id for entry in queue_entries]
        # pprint(sample_ids)
        # return sample_ids


class New(Resource):

    def get(self):
        id = request.args.get("sample", default=0, type=int)
        label = random.randint(0, 2)
        queue = process_dict["iris"][1]
        data = {"id": id, "label": label}
        queue.put(data)
        return data
