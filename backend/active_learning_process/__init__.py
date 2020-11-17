import json
from sqlalchemy import func as db_functions

from .al_oracle import ParallelOracle
from .al_process import ALProcess
from .process_management import manager
from ..config import logger, db
from ..models import Dataset, Association, Sample, ActiveLearningConfig


def should_label_random_sample(dataset: Dataset, random_sample_every: int = 10) -> bool:
    number_of_labeled_samples = (
        db.query(Association).join(Association.sample)
        .filter(Sample.dataset == dataset)
        .count()
    )
    return number_of_labeled_samples % random_sample_every == 0


def get_random_unlabelled_sample(dataset: Dataset) -> Sample:
    return (
        db.query(Sample).filter(Sample.dataset == dataset, ~Sample.associations.any())
        .order_by(db_functions.random())
        .first()
    )


def get_next_sample(dataset: Dataset) -> Sample:
    config = dataset.get_config()

    if should_label_random_sample(dataset=dataset, random_sample_every=config.RANDOM_SAMPLE_EVERY):
        return get_random_unlabelled_sample(dataset)

    # Retrieve pipe endpoint from process manager
    process_resources = manager.get_or_else_load(dataset)
    pipe_endpoint = process_resources["pipe"]

    if pipe_endpoint.poll(config.TIMEOUT_FOR_WORKER):
        logger.info("Found new data points")
        next_sample_id = pipe_endpoint.recv()
        return db.query(Sample).get(next_sample_id)
    else:
        # Send back a random label anyway for testing purposes
        logger.info("No samples available from AL, send back a random sample instead")
        return get_random_unlabelled_sample(dataset)


def notify_about_new_sample(
    dataset: Dataset, user_id: int, sample_id: int, label_id: int
) -> None:
    config = dataset.get_config()

    if config.RANDOM_SAMPLE_EVERY is 0:
        return

    process_resources = manager.get_or_else_load(dataset_id=dataset.id)
    pipe_endpoint = process_resources["pipe"]
    pipe_endpoint.send({"id": sample_id, "label": label_id, "user": user_id})
