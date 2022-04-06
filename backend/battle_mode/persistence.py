import ast
import pickle
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, List

import pandas as pd
from pydantic import BaseModel

from .battle_manager import BattleAnalyzer, BattleManager
from ..config import logger
from ..importing import DATA_PATH
from ..models import ALBattleConfig, MetaData, ExperimentResults,MetricsDFKeys


class ExperimentMetaPersistence(BaseModel):
    dataset_id: int
    config: ALBattleConfig
    path: Path


@dataclass
class ExperimentResultsPersistence:
    meta_data: List[MetaData]
    classes: List[str]
    correct_label_as_idx: Dict[int, int]
    initially_labeled: List[int]


class Persistence:
    data_path = DATA_PATH / 'experiments'
    persisted_experiments: Dict[int, ExperimentMetaPersistence] = {}

    def __init__(self):
        raise ValueError("Persistence should not be instantiated.")

    @staticmethod
    def restore():
        if not Persistence.data_path.exists():
            Persistence.data_path.mkdir(parents=True)
            return
        for path in Persistence.data_path.iterdir():
            if not path.is_dir():
                logger.warn(f"Unexpected file found in experiments: {path}")
                continue
            try:
                exp_id = int(path.name)
                meta = Persistence._load_meta(path)
                Persistence.persisted_experiments[exp_id] = meta
            except ValueError:
                logger.warn(f"Directory with invalid name in experiments: {path}")
        if len(Persistence.persisted_experiments) > 0:
            highest_persisted_id = max(Persistence.persisted_experiments.keys())
            BattleManager._experiment_id_counter = \
                max(BattleManager.get_experiment_id_counter(), highest_persisted_id + 1)

    @staticmethod
    def delete(experiment_id: int):
        meta: ExperimentMetaPersistence = Persistence.persisted_experiments[experiment_id]
        path: Path = meta.path
        shutil.rmtree(path)
        del Persistence.persisted_experiments[experiment_id]

    @staticmethod
    def get_storage_overview():
        return Persistence.persisted_experiments

    @staticmethod
    def store_finished_experiments(exp_id: int, finished_manager: BattleAnalyzer):
        Persistence.data_path.mkdir(parents=True, exist_ok=True)  # ensure data_path exists
        exp_path = Persistence.data_path / str(exp_id)
        if exp_path.exists():
            logger.warn("Overwriting persisted experiment: " + str(exp_id))
        exp_path.mkdir(exist_ok=True)
        cb_sample_path = exp_path / 'cb_sample'
        finished_manager.cb_sample.to_csv(cb_sample_path.absolute())
        meta = ExperimentMetaPersistence(
            dataset_id=finished_manager.dataset_id,
            config=finished_manager.config,
            path=exp_path)
        Persistence._store_meta(exp_path, meta)
        Persistence._store_experiments(exp_path, finished_manager.results[0], finished_manager.results[1])
        Persistence.persisted_experiments[exp_id] = meta

    @staticmethod
    def _store_meta(exp_path: Path, meta: ExperimentMetaPersistence):
        meta_path = exp_path / 'meta'
        with meta_path.open(mode='wb') as file:
            pickle.dump(meta, file)

    @staticmethod
    def _store_experiments(exp_path: Path, exp_one: ExperimentResults, exp_two: ExperimentResults):
        # Make sure /data exists
        # Create Folder with name = id
        # Create Folder for exp_one and exp_two
        # each dataframe from ExperimentResults is a csv
        # everything else gets pickled
        exp_one_path = exp_path / str(1)
        exp_two_path = exp_path / str(2)
        Persistence._serialize_single_exp(exp_one, exp_one_path)
        Persistence._serialize_single_exp(exp_two, exp_two_path)

    @staticmethod
    def _serialize_single_exp(exp_obj: ExperimentResults, path: Path):
        if not path.exists():
            path.mkdir()
        raw_predictions_path = path / 'raw_predictions'
        exp_obj.raw_predictions.to_csv(raw_predictions_path.absolute())

        cb_predictions_path = path / 'cb_predictions'
        exp_obj.cb_predictions.to_csv(cb_predictions_path.absolute())

        metric_scores_path = path / 'metric_scores'
        exp_obj.metric_scores.to_csv(metric_scores_path.absolute())

        pickle_file_path = path / 'pickle'
        # dont save pandas dataframes
        persisted_results = ExperimentResultsPersistence(
            classes=exp_obj.classes,
            initially_labeled=exp_obj.initially_labeled,
            correct_label_as_idx=exp_obj.correct_label_as_idx,
            meta_data=exp_obj.meta_data
        )
        with pickle_file_path.open(mode='wb') as file:
            pickle.dump(obj=persisted_results, file=file)

    @staticmethod
    def _deserialize_single_exp(path: Path) -> ExperimentResults:
        # minus one because the index column is represented too
        raw_predictions = Persistence._deserialize_predictions_dataframe(path, 'raw_predictions')

        cb_predictions = Persistence._deserialize_predictions_dataframe(path, 'cb_predictions')

        metric_scores_path = path / 'metric_scores'
        metric_scores = pd.read_csv(metric_scores_path.absolute(), index_col=0)
        metric_scores.columns = metric_scores.columns.map(MetricsDFKeys)

        pickle_file_path = path / 'pickle'

        with pickle_file_path.open(mode='rb') as file:
            persisted_obj: ExperimentResultsPersistence = pickle.load(file=file)
            exp_results = ExperimentResults(
                raw_predictions=raw_predictions,
                initially_labeled=persisted_obj.initially_labeled,
                cb_predictions=cb_predictions,
                metric_scores=metric_scores,
                correct_label_as_idx=persisted_obj.correct_label_as_idx,
                meta_data=persisted_obj.meta_data,
                classes=persisted_obj.classes
            )
            return exp_results

    @staticmethod
    def _deserialize_predictions_dataframe(path: Path, name: str):
        dataframe_path = path / name
        # convert all tuples to real tuples
        nbr_of_columns = len(dataframe_path.open(mode='r').readline().split(","))
        dataframe = pd.read_csv(
            dataframe_path.absolute(),
            index_col=0,
            converters={col: ast.literal_eval for col in range(nbr_of_columns)}
        )
        # columns should be integer instead of strings
        dataframe.columns = dataframe.columns.astype(int)
        return dataframe

    @staticmethod
    def _load_experiments(exp_path: Path) -> Tuple[ExperimentResults, ExperimentResults]:
        exp_one_path = exp_path / str(1)
        exp_two_path = exp_path / str(2)
        if (not exp_one_path.exists()) or (not exp_two_path.exists()):
            raise ValueError("Persistence structure corrupted")
        exp_one = Persistence._deserialize_single_exp(exp_one_path)
        exp_two = Persistence._deserialize_single_exp(exp_two_path)
        return exp_one, exp_two

    @staticmethod
    def _load_meta(exp_path: Path):
        meta_path = exp_path / 'meta'
        with meta_path.open(mode='rb') as file:
            meta: ExperimentMetaPersistence = pickle.load(file)
            return meta

    @staticmethod
    def load_finished_experiments(exp_id: int) -> BattleAnalyzer:

        if exp_id not in Persistence.persisted_experiments:
            raise ValueError(f"Experiment for ID = {exp_id} does not exist")
        exp_path = Persistence.persisted_experiments[exp_id].path

        cb_sample_path = exp_path / 'cb_sample'
        cb_sample = pd.read_csv(cb_sample_path.absolute(), index_col=0)
        exp_one, exp_two = Persistence._load_experiments(exp_path)
        meta = Persistence._load_meta(exp_path)
        return BattleAnalyzer(
            experiment_id=exp_id,
            dataset_id=meta.dataset_id,
            config=meta.config,
            cb_sample=cb_sample,
            result_one=exp_one,
            result_two=exp_two)


# restore all experiments on load
Persistence.restore()
