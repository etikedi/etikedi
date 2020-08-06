from flask_praetorian import auth_required, roles_required
from flask_restful import abort, Resource

from ..config import app, api
from ..models import Label, LabelSchema


class LabelAPI(Resource):
    method_decorators = {"get": [auth_required], "post": [roles_required("admin")]}

    def get(self, dataset_id):
        """
        This function responds to a request for /api/int:dataset_id/labels
        with the complete lists of data sets

        :return:        json string of list of labels for a data set
        """
        labels = Label.query.filter(Label.dataset_id == dataset_id)

        if labels is None:
            abort(
                404,
                "Labels not found for data set: {dataset_id}".format(
                    dataset_id=dataset_id
                ),
            )

        return LabelSchema(many=True).dump(labels)

    def post(self):
        """ TODO: Allow adding labels for admins """
        pass


api.add_resource(LabelAPI, "/api/datasets/<int:dataset_id>/labels")


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
