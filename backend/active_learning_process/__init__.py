from sqlalchemy import func as db_functions

from .al_oracle import ParallelOracle
from .al_process import ALProcess
from .process_management import manager
from ..aergia import logger
from ..models import Dataset, Association, Sample


def should_label_random_sample(dataset: Dataset, random_sample_every: int = 10) -> bool:
    number_of_labeled_samples = (
        Association.query.join(Association.sample)
            .filter(Sample.dataset == dataset)
            .count()
    )
    return number_of_labeled_samples % random_sample_every == 0


def get_random_unlabelled_sample(dataset: Dataset) -> Sample:
    return (
        Sample.query.filter(Sample.dataset == dataset, ~Sample.associations.any())
            .order_by(db_functions.random())
            .first()
    )


def get_next_sample(dataset: Dataset) -> Sample:
    # Retrieve pipe endpoint from process manager
    if should_label_random_sample(dataset=dataset):
        return get_random_unlabelled_sample(dataset)

    process_resources = manager.get_or_else_load(dataset)
    pipe_endpoint = process_resources["pipe"]

    if pipe_endpoint.poll(60):
        logger.info("Found new datapoints")
        next_sample_id = pipe_endpoint.recv()
        return Sample.query.get(next_sample_id)
    else:
        # Send back a random label anyway for testing purposes
        logger.info("No samples available from AL, send back a random sample instead")
        return get_random_unlabelled_sample(dataset)


def notify_about_new_sample(dataset: Dataset, user_id: int, sample_id: int, label_id: int) -> None:
    process_resources = manager.get_or_else_load(dataset_id=dataset.id)
    pipe_endpoint = process_resources["pipe"]
    pipe_endpoint.send({"id": sample_id, "label": label_id, "user": user_id})
