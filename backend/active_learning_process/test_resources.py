from pprint import pprint

from flask_restful import Resource

from active_learning_process.al_process import ALProcess
from active_learning_process.db_functions import to_be_labeled


class Start(Resource):
    def get(self):
        aL = ALProcess("iris")
        aL.start()
        return "Started"

class Index(Resource):

    def get(self):
        queue_entries = to_be_labeled()
        sample_ids = [entry.id for entry in queue_entries]
        pprint(sample_ids)
        return sample_ids

