from typing import List, Optional, Union

from fastapi import Depends, UploadFile, File, Form, HTTPException, APIRouter, status, Query, Response
from sqlalchemy import func, not_, select
from sqlalchemy.orm import aliased

from ..config import db
from ..importing.generic import import_dataset
from ..models import DatasetStatistics, Dataset, DatasetDTO, User, Table, Image, Text, SampleDTO, Sample, Association, \
    Label, SampleDTOwLabel
from ..utils import number_of_labelled_samples, number_of_total_samples, number_of_features, get_current_active_user, \
    get_current_active_admin
from ..worker import manager

dataset_router = APIRouter()


@dataset_router.get("", response_model=List[DatasetDTO])
def get_datasets(user: User = Depends(get_current_active_user)):
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
        user: User = Depends(get_current_active_user),
):
    if sample_type not in ["table", "image", "text"]:
        raise HTTPException(status_code=400, detail="Not a valid sample type")
    sample_class = {"table": Table, "image": Image, "text": Text}[sample_type]

    features.file.rollover()
    contents.file.rollover()

    dataset, number_of_samples = import_dataset(
        name=name,
        sample_class=sample_class,
        features=features.file,
        content=contents.file,
        user=user,
        ensure_incomplete=True,
    )

    return dataset


@dataset_router.delete("/{dataset_id}", response_model=DatasetDTO)
def delete_dataset(
        dataset_id: int,
        current_user: User = Depends(get_current_active_admin)
):
    if current_user.roles != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the authorization to delete a dataset!"
        )

    dataset = get_dataset_or_throw(dataset_id)

    db.delete(dataset)
    db.commit()
    return dataset


@dataset_router.get("/{dataset_id}/first_sample", response_model=SampleDTO)
def get_first_sample(dataset_id: int, user: User = Depends(get_current_active_user)):
    dataset = get_dataset_or_throw(dataset_id)

    worker = manager.get_or_else_load(dataset)
    first_sample_id = worker.get_next_sample_id()
    first_sample = db.get(Sample, first_sample_id)
    if not first_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the first sample.",
        )

    return first_sample


@dataset_router.get("/{dataset_id}/samples/", response_model=List[SampleDTOwLabel])
def get_filtered_samples(
        response: Response,
        dataset_id: int,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        labels: Optional[List[int]] = Query(None),
        users: Optional[List[int]] = Query(None),
        labeled: Optional[bool] = None,
        free_text: Optional[Union[str, bytes]] = None,
        divided_labels: Optional[bool] = None,
        user: User = Depends(get_current_active_user)):
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

    :param user:                the currently active user -> needed for authentication-check\\
    :return:                    list of samples
    """

    # return only current associations, if changed code needs to be adapted
    only_current_associations = True

    dataset = get_dataset_or_throw(dataset_id)

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
            .join(association2, Sample.id == association2.sample_id) \
            .filter(association1.is_current == only_current_associations) \
            .filter(association1.is_current == only_current_associations)

        # use query as subquery to apply other filters (eg. for labels or users)
        sub_query = query.with_entities(Sample.id).subquery()

        # build new query
        query = base_query \
            .filter(not_(association1.label_id == association2.label_id)) \
            .filter(Sample.id.in_(sub_query)) \
            .group_by(Sample.id).having(func.count(association1.label_id) > 1) \
            .order_by(func.count(association1.label_id).desc())

    # only return samples with no label or a current label
    # All Samples with a current label
    with_current_association = db.query(Sample.id)\
        .join(Association, Sample.id == Association.sample_id)\
        .filter(Association.is_current == only_current_associations)
    # All Samples with a label
    with_association = db.query(Sample.id)\
        .join(Association, Sample.id == Association.sample_id)\
        .subquery()
    # All Samples without any labels
    without_association = db.query(Sample.id)\
        .filter(Sample.id.notin_(with_association))

    valid_samples = with_current_association.union(without_association)

    query = query.filter(Sample.id.in_(valid_samples))

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

    samples = query.all()
    return samples


@dataset_router.get('/{dataset_id}/metrics/')
def get_worker_metrics(dataset_id: int, user=Depends(get_current_active_user)):
    """
    Returns a dictionary of lists.

    The ith-entry in every list represents the value of this metric for the ith-run of the active learning worker.
    """
    dataset = get_dataset_or_throw(dataset_id)

    worker = manager.get(dataset)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No worker found for the dataset"
        )

    return worker.metrics


@dataset_router.get('/{dataset_id}/features', response_model=List[str])
def get_dataset_features(dataset_id: int):
    """Return all feature names for this dataset."""
    dataset = get_dataset_or_throw(dataset_id)
    return dataset.feature_names.split(',')


def get_dataset_or_throw(dataset_id: int) -> Dataset:
    dataset = db.query(Dataset).get(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found for id: {}.".format(dataset_id)
        )
    return dataset
