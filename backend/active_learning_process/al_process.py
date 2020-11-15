import multiprocessing

from .al_oracle import ParallelOracle
from .prepare import prepare_dataset_for_active_learning
from ..active_learning.al_cycle_wrapper import train_al
from ..active_learning.experiment_setup_lib import init_logger
from ..models import Dataset


class ALProcess(multiprocessing.Process):
    """
    Extension of multiprocessing. Process as a wrapper class for asynchronous execution of active-learning
    code lifecycle.
    """

    def __init__(self, config, dataset_id: int, pipe_endpoint):
        super().__init__()
        self.dataset_id = dataset_id
        self.config = config
        self.pipe_endpoint = pipe_endpoint

    def run(self):
        """
        This methods represents the entry point to the active-learning code.
        Before it can be started, data has to get retrieved from database.
        This is done via a member of this class which allows an unambiguously identification of the queried dataset.
        After the data preparation is done, a BaseOracle object is created and - including with the configuration and
        data -  fed to the active learning code.
        """
        init_logger("log.txt")

        dataset = Dataset.query.filter_by(id=self.dataset_id).first()
        df = prepare_dataset_for_active_learning(dataset)

        (_, _, metrics_per_al_cycle, data_storage, _) = train_al(
            hyper_parameters=self.config,
            df=df,
            oracle=ParallelOracle(pipe_endpoint=self.pipe_endpoint)
        )
