from typing import List, Optional, Union

from fastapi import Depends, UploadFile, File, Form, HTTPException, APIRouter, status, Query, Response
from sqlalchemy import func

from ..worker import get_next_sample
from ..config import db
from ..importing import import_dataset
from ..models import Dataset, DatasetDTO, User, Table, Image, Text, SampleDTO, Sample, Association, Label
from ..utils import get_current_active_user

dataset_router = APIRouter()


@dataset_router.get("", response_model=List[DatasetDTO])
def get_datasets():
    datasets = db.query(Dataset).all()
    return datasets


@dataset_router.post("", response_model=DatasetDTO)
def create_dataset(
        name: str = Form(...),
        sample_type: str = Form(...),
        features: UploadFile = File(...),
        contents: UploadFile = File(...),
        current_user: User = Depends(get_current_active_user),
):
    if sample_type not in ["table", "image", "text"]:
        raise HTTPException(status_code=400, detail="Not a valid sample type")
    sample_class = {"table": Table, "image": Image, "text": Text}[sample_type]

    dataset, number_of_samples = import_dataset(
        name=name,
        sample_class=sample_class,
        features=features.file,
        content=contents.file,
        user=current_user,
        ensure_incomplete=True,
    )

    return dataset


@dataset_router.get("/{dataset_id}/first_sample", response_model=SampleDTO)
def get_first_sample(dataset_id: int):
    dataset = db.query(Dataset).get(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found for id: {}.".format(dataset_id)
        )

    first_sample = get_next_sample(dataset)
    if not first_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the first sample.",
        )
    first_sample.ensure_string_content()

    return first_sample


@dataset_router.get("/{dataset_id}/samples/", response_model=List[SampleDTO])
def get_filtered_samples(
        response: Response,
        dataset_id: int,
        total_amount: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        labels: Optional[List[int]] = Query(None),
        users: Optional[List[int]] = Query(None),
        labeled: Optional[bool] = None,
        free_text: Optional[Union[str, bytes]] = None,
        divided_labels: Optional[bool] = None):
    """
    :param dataset_id:          dataset_id for dataset\\
    :param limit:               number of samples per page\\
    :param page:                number of page that should be fetched (beginning with 0)\\
    :param total_amount:        sets max limit how many samples should be returned\\

    :param labeled:             return only labeled samples (true) / unlabeled samples (false)\\
    :param labels:              list of label_ids to filter for add each label with label = label_id\\
    :param divided_labels:      search only for samples, which different users labeled differently\\

    :param users:               list of user_ids to filter for add each user with users = user_id\\
    :param free_text:           freetext search (only one word)\\
    :return:                    list of samples
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found for id: {}.".format(dataset_id)
        )

    query = db.query(Sample).filter(Sample.dataset_id == dataset_id)

    # JOIN table association for later use
    if labels or users or divided_labels:
        query = query.join(Association, Sample.id == Association.sample_id)

    # filter for labels
    if labels:
        for label_id in labels:
            label = db.query(Label).get(label_id)
            if not label:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Label not found for id: {}.".format(label_id),
                )
        query = query.filter(Association.label_id.in_(labels))

    # filter for users who labeled the sample
    if users:
        for user_id in users:
            user = db.query(User).get(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found for id: {}.".format(user_id),
                )
        query = query.filter(Association.user_id.in_(users))

    # filter for only labeled or unlabeled datasets
    if labeled is not None:
        if labeled:
            query = query.join(Association, Sample.id == Association.sample_id)
        else:
            if users or labels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot process unlabeled Samples if filters for Labels or Users are set.",
                )
            query = query.filter(Sample.dataset_id == 1, ~Sample.associations.any())

    # text search
    if free_text:
        sample = db.query(Sample).filter(Sample.dataset_id == dataset_id).first()
        content_type = sample.type

        if content_type == "text":
            query = query.join(Text).filter(Text.content.like('%{}%'.format(free_text)))

    # filter for divided labels (sample has more than 1 label)
    if divided_labels:
        query = query.group_by(Sample.id).having(func.count(Association.label_id) > 1).order_by(
            func.count(Association.label_id))

    # limit number of returned elements and paging
    if page is not None and limit:
        total_elements = query.count()
        response.headers["X-Total"] = "{}".format(total_elements)
        lower_limit = page * limit
        upper_limit = page * limit + limit
        query = query.order_by(Sample.id).slice(lower_limit, upper_limit)

    if total_amount and not (page is not None and limit):
        query = query.limit(total_amount)
        return query.all()

    return query.all()
