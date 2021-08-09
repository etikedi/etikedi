import random
from multiprocessing.connection import Pipe
from typing import Set

from ..config import logger, db
from .process import ActiveLearningProcess, SampleID, EventType
from ..models import Dataset


class AlWorker:

    def __init__(self, dataset_id: int):
        self.dataset_id = dataset_id
        self._create_process()
        self.requested_sample_ids: Set[SampleID] = set()
        self.suggested_sample_ids: Set[SampleID] = set()
        self.pending_request = False
        self.start_process()

    def _create_process(self):
        self.pipe_endpoint, other_endpoint = Pipe(duplex=True)
        self.process = ActiveLearningProcess(
            dataset_id=self.dataset_id,
            pipe_endpoint=other_endpoint)

    def start_process(self):
        logger.debug(f"Starting process for ID: {self.dataset_id}")
        self.process.start()
        self._request_samples_proactive()

    def stop_process(self):
        if self.process.is_alive():
            self.pipe_endpoint.send({
                'event': EventType.STOP
            })
            self.process.join(None)
            self.pipe_endpoint.close()
            self.process.close()

    def restart_process(self):
        self.stop_process()
        self._create_process()
        self.start_process()

    def __del__(self):
        try:  # __del__ could be called before __init__ is finished
            self.process.join()
            self.process.close()
        except AttributeError:
            pass

    def get_next_sample_id(self) -> SampleID:
        if len(self.requested_sample_ids) != 0:
            logger.info("Suggested sample according to QueryStrategy")
            sample_id: SampleID = self.requested_sample_ids.pop()
        else:
            self.requested_sample_ids.update(self.recv_else_random())
            sample_id = self.requested_sample_ids.pop()
        # request more samples now to prevent random samples
        if len(self.requested_sample_ids) < 2:
            self._request_samples_proactive()

        self.suggested_sample_ids.add(sample_id)
        return sample_id

    def recv_else_random(self) -> Set[SampleID]:
        assert self.process.is_alive()
        # if pipe is empty send new request
        if self.pipe_endpoint.poll():
            message = self.pipe_endpoint.recv()
            if message['event'] == EventType.REQUEST:
                self.pending_request = False
                return set(message['sample_ids'])
            else:
                raise RuntimeError(f"Event type ({message['event']}) could not be handled")
        else:
            # wait for response
            logger.info("Suggested random sample")
            # use random sample if nothing received TODO improve db access time
            samples = db.get(Dataset, self.dataset_id).samples
            unlabeled_ids = list(map(lambda sample: sample.id, filter(lambda sample: sample.labels == [], samples)))
            return {random.choice(unlabeled_ids)}

    def _request_samples_proactive(self) -> None:
        assert self.process.is_alive()
        logger.debug("Sending sample request")
        if not self.pending_request:  # only request if not already done
            self.pipe_endpoint.send({
                'event': EventType.REQUEST,
            })
            self.pending_request = True

    def add_sample_label(self, sample_id: SampleID) -> None:
        if sample_id in self.suggested_sample_ids:
            self.suggested_sample_ids.remove(sample_id)
        else:
            logger.warning("Sample was never suggested")

        self.pipe_endpoint.send({
            'event': EventType.ADD,
            'sample_id': sample_id
        })

    def remove_sample_label(self, sample_id: SampleID) -> None:
        self.pipe_endpoint.send({
            'event': EventType.REMOVE,
            'sample_id': sample_id
        })
