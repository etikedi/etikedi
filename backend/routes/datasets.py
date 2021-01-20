from typing import List, Optional, Union

from fastapi import Depends, UploadFile, File, Form, HTTPException, APIRouter, status, Query, Response
from sqlalchemy import func, not_, select
from sqlalchemy.orm import aliased

from ..config import db
from ..importing import import_dataset
from ..models import DatasetStatistics, Dataset, DatasetDTO, User, Table, Image, Text, SampleDTO, Sample, Association, \
    Label
from ..utils import number_of_labelled_samples, number_of_total_samples, number_of_features, get_current_active_user
from ..worker import get_next_sample

dataset_router = APIRouter()


@dataset_router.get("", response_model=List[DatasetDTO])
def get_datasets():
    datasets = db.query(Dataset).all()

    for dataset in datasets:
        dataset.statistics = DatasetStatistics(
            total_samples=number_of_total_samples(dataset),
            labelled_samples=number_of_labelled_samples(dataset),
            features=number_of_features(dataset),
            labels=len(dataset.labels)
        )

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
        page: Optional[int] = None,
        limit: Optional[int] = None,
        labels: Optional[List[int]] = Query(None),
        users: Optional[List[int]] = Query(None),
        labeled: Optional[bool] = None,
        free_text: Optional[Union[str, bytes]] = None,
        divided_labels: Optional[bool] = None):
    """
    NOT for usage in connection with Active Learning!

    :param response:            gets Response Header Object from FastAPI, dont fill\\
    :param dataset_id:          dataset_id for dataset\\

    :param limit:               number of samples per page\\
    :param page:                number of page that should be fetched (beginning with 0) \\

    both limit and page need to be filled for paging, returns Total number of elements in the Header in X-Total \\

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
    if labels or users:
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
            if not (labels or users):
                query = query.join(Association, Sample.id == Association.sample_id)
        else:
            if users or labels or divided_labels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot process unlabeled Samples if filters for Labels or Users are set.",
                )
            query = query.filter(Sample.dataset_id == dataset_id, ~Sample.associations.any())

    # text search
    if free_text:
        # prepare text
        free_text = free_text.replace(" ", " & ")

        sample = db.query(Sample).filter(Sample.dataset_id == dataset_id).first()
        content_type = sample.type

        # text search only for content type 'text' and 'table'
        if content_type == "text":
            matched_tables = select([Text.id]).where(Text.content.match('{}'.format(free_text)))
            query = query.join(Text).filter(Text.id.in_(matched_tables))
        elif content_type == "table":
            matched_tables = select([Table.id]).where(Table.content.match('{}'.format(free_text)))
            query = query.join(Table).filter(Table.id.in_(matched_tables))
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The Dataset with id {} does not have text to search as content.".format(dataset_id),
            )

    # filter for divided labels (sample has more than 1 label)
    if divided_labels:
        # rebuild base query, join association 2x with alias
        association1 = aliased(Association)
        association2 = aliased(Association)

        base_query = db.query(Sample) \
            .filter(Sample.dataset_id == dataset_id) \
            .join(association1, Sample.id == association1.sample_id) \
            .join(association2, Sample.id == association2.sample_id)

        # use query as subquery to apply other filters (eg. for labels or users)
        sub_query = query.with_entities(Sample.id).subquery()

        # build new query
        query = base_query \
            .filter(not_(association1.label_id == association2.label_id)) \
            .filter(Sample.id.in_(sub_query)) \
            .group_by(Sample.id).having(func.count(association1.label_id) > 1) \
            .order_by(func.count(association1.label_id).desc())

    # limit number of returned elements and paging, return total_elements in header
    if page is not None and limit:
        if page < 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page number needs to be 0 or greater. Page number was: {}.".format(page),
            )

        total_elements = query.count()
        response.headers["X-Total"] = "{}".format(total_elements)
        lower_limit = page * limit
        upper_limit = page * limit + limit
        query = query.order_by(Sample.id).slice(lower_limit, upper_limit)

    return query.all()
