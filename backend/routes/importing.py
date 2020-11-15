# from flask import request
# from flask_praetorian import auth_required, current_user
# from flask_restful import Resource
#
# from ..importing import import_dataset
# from ..config import db, api
# from ..models import Dataset, Table, Text, Image, Sample
#
from ..config import app


@app.post("/api/datasets/{dataset_id}/import", tags=['datasets'])
async def post_import(dataset_id: int):
    return "TODO"
#
# class ImportAPI(Resource):
#     method_decorators = [auth_required]
#
#     def post(self, dataset_id: int):
#         dataset = Dataset.query.get(dataset_id)
#         sample_type = request.form["sample_type"].lower()
#         sample_class = {"table": Table, "image": Image, "text": Text}[sample_type]
#
#         import_dataset(
#             dataset=dataset,
#             sample_class=sample_class,
#             features=request.files["features"],
#             content=request.files["content"],
#             user=current_user(),
#             ensure_incomplete=True,
#         )
#
#         return (
#             db.session.query(Sample.id).filter(Sample.dataset == dataset).count(),
#             200,
#         )
#
#
# api.add_resource(ImportAPI, "/api/datasets/<int:dataset_id>/import")
