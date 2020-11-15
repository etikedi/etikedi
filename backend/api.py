import json
from datetime import timedelta
from sqlite3 import IntegrityError
from typing import List

from fastapi.security import OAuth2PasswordRequestForm
from marshmallow import ValidationError
from pydantic import dataclasses
from sqlalchemy.orm import Session

from backend.active_learning_process import get_next_sample, notify_about_new_sample, manager
from backend.config import ALConfigSchema
from backend.database import get_db
from backend.models import User, Dataset, Label, Association
from backend.models.datatypes import SampleSchema, Sample, Table, Image, Text
from backend.models.schemas import Token, DatasetBase, LabelSchema
from fastapi import APIRouter, Depends, HTTPException, status

from backend.user_management import authenticate_user, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    get_current_active_user


router = APIRouter()

##############################################################################################################
#                                               Users                                                        #
##############################################################################################################


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


##############################################################################################################
#                                               Dataset                                                      #
##############################################################################################################

@router.get("/api/datasets", response_model=List[DatasetBase])
async def get_dataset_list():
    """
    This function responds to a request for /api/datasets
    with the complete lists of data sets

    :return:        list of datasets (e.g. dwtc, religious_texts...)
    """
    datasets = Dataset.query.all()
    return DatasetBase(many=True).dump(datasets)


@router.post("/api/datasets", response_model=DatasetBase)
async def post_dataset_list(dataset: DatasetBase, db: Session = Depends(get_db)):
    try:
        new_dataset = Dataset(name=dataset.name)
        db.add(new_dataset)
        db.commit()
        return DatasetBase().dump(new_dataset)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while attempting to create the dataset."
        )


@router.get("/api/datasets/{dataset_id}", response_model=DatasetBase)
async def get_dataset_details(dataset_id: int):
    """
    This function responds to a request for /api/int:dataset_id
    with the next data sample of data set that should get labeled

    :param dataset_id:   ID of data set to find
    :return:            data set matching ID
    """
    dataset = Dataset.query.filter_by(id=dataset_id).first()

    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Dataset found for this id.")

    next_sample = get_next_sample(dataset)
    if not next_sample:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while searching for the requested sample."
        )

    next_sample.ensure_string_content()
    return SampleSchema().dump(next_sample), 200


@router.post("/api/datasets/{dataset_id}", response_model=DatasetBase)
async def post_dataset_details(dataset_id: int):
    """ TODO: Update name of dataset. """
    pass


##############################################################################################################
#                                                   Labels                                                   #
##############################################################################################################


@router.get("/api/datasets/{dataset_id}/labels")
async def get_labels(dataset_id: int):
    """
    This function responds to a request for /api/int:dataset_id/labels
    with the complete lists of data sets

    :return:        json string of list of labels for a data set
    """
    labels = Label.query.filter(Label.dataset_id == dataset_id)

    if labels is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Labels not found for data set: {}".format(dataset_id)
        )

    return LabelSchema(many=True).dump(labels)


@router.post("/api/datasets/{dataset_id}/labels")
async def post_labels(dataset_id: int):
    """ TODO: Allow adding labels for admins """
    pass


##############################################################################################################
#                                                   Samples                                                  #
##############################################################################################################

@router.get("/api/sample/{sample_id}")
async def get_sample(sample_id: int):
    sample = Sample.query.filter_by(id=sample_id).first()
    if sample is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found for id: {}.".format(sample_id)
        )

    return SampleSchema().dump(sample)


@router.post("/api/sample/{sample_id}")
async def post_sample(sample_id: int, label_id: int, db: Session = Depends(get_db)):
    """
    This function responds to a request for /api/sample/int:data_sample_id
    with the next data sample of data set that should get labeled

    :param sample_id:   ID of data sample to find
    :return:            data set matching ID
    """
    user = get_current_active_user()

    if not can_assign(sample_id, label_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't assign label to sample."
        )

    try:
        new_association = Association(
            sample_id=sample_id, label_id=label_id, user_id=user.id
        )
        db.add(new_association)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    # Retrieve pipe endpoint for process with corresponding dataset_id and send new label
    dataset = Sample.query.get(sample_id).dataset

    notify_about_new_sample(
        dataset=dataset, user_id=user.id, sample_id=sample_id, label_id=label_id
    )

    next_sample = get_next_sample(dataset)
    if not next_sample:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error retrieving the next sample."
        )
    next_sample.ensure_string_content()
    return SampleSchema().dump(next_sample), 201


def can_assign(sample_id: int, label_id: int, db: Session = Depends(get_db)):
    return bool(
        db.query(Dataset, Sample, Label)
            .filter(Dataset.id == Sample.dataset_id)
            .filter(Dataset.id == Label.dataset_id)
            .filter(Sample.id == sample_id)
            .filter(Label.id == label_id)
            .count()
    )


##############################################################################################################
#                                                   Config                                                   #
##############################################################################################################

@router.get("/api/datasets/{dataset_id}/config")
async def get_dataset_config(dataset_id: int):
    """ Return the current configuration for the given dataset. """
    dataset = Dataset.query.get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No config found."
        )

    return json.loads(dataset.config)


@router.post("/api/datasets/{dataset_id}/config")
async def post_dataset_config(dataset_id: int, items, db: Session = Depends(get_db)):
    """ Update the configuration for the given dataset. Implies a restart of the AL process. """
    dataset = Dataset.query.get(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset found."
        )

    try:
        new_config = ALConfigSchema().load(
            {k.upper(): v for k, v in items}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.messages
        )

    dataset.config = json.dumps(dataclasses.asdict(new_config))
    db.commit()

    manager.restart_with_config(dataset, json.loads(dataset.config))

    return None, 204


##############################################################################################################
#                                                   Importing                                                #
##############################################################################################################

@router.post("/api/datasets/{dataset_id}/import")
async def post_import(dataset_id: int, sample_type: str, db: Session = Depends(get_db)):
    dataset = Dataset.query.get(dataset_id)
    sample_class = {"table": Table, "image": Image, "text": Text}[sample_type]

    # TODO
    # import_dataset(
    #     dataset=dataset,
    #     sample_class=sample_class,
    #     features=request.files["features"],
    #     content=request.files["content"],
    #     user=get_current_user(),
    #     ensure_incomplete=True,
    # )

    return db.query(Sample.id).filter(Sample.dataset == dataset).count(), 200
