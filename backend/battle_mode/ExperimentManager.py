from __future__ import annotations  # necessary in order to use ExperimentManager as type hint

from dataclasses import dataclass
from multiprocessing import Queue
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from .additional_experiment_validation import validate_else_throw
from .experiment import ALExperimentProcess, MetricsDFKeys, EventType, ResultType
from ..config import db, logger
from ..models import ALBattleConfig, Metric, Status, Dataset, Sample, MetricIteration, MetricScoresIteration
from ..utils import ValidationError, zip_unequal


# Dataclasses
@dataclass
class ClassificationBoundariesDTO:
    reduced_features: pd.DataFrame
    exp_one_iterations: List[pd.DataFrame]
    exp_two_iterations: List[pd.DataFrame]


class ExperimentManager:
    """Manages (asynchronous) execution of two AL-strategies"""

    _manager: Dict[int, ExperimentManager] = {}

    @staticmethod
    def has_manager(dataset_id: int):
        return dataset_id in ExperimentManager._manager

    @staticmethod
    def get_manager(dataset_id):
        return ExperimentManager._manager[dataset_id]

    def __init__(self, dataset_id: int, battle_config: ALBattleConfig):
        self.dataset_id: int = dataset_id
        validate_else_throw(dataset_id, battle_config)
        self.config = battle_config
        self.started_flags: List[bool, bool] = [False, False]
        self.setup_completed_flags: List[bool, bool] = [False, False]
        self.finished_flags: List[bool, bool] = [False, False]
        self.results: List[Optional[ResultType], Optional[ResultType]] = [None, None]
        self.last_reported_time: Optional[Tuple[float, bool]] = None  # reported time, true if experiment one
        self.metric: Optional[Metric] = None
        self.queues = [Queue(), Queue()]
        self.cb_sample = self._classification_boundaries_raster(100)
        self.experiments: List[ALExperimentProcess] = [
            ALExperimentProcess(i, dataset_id, self.config, self.queues[i], self.cb_sample) for i in [0, 1]]
        if dataset_id in ExperimentManager._manager:
            logger.warn(f"Replacing existent manager for id {dataset_id}")
            ExperimentManager._manager[dataset_id].terminate()
        ExperimentManager._manager[dataset_id] = self

    def _classification_boundaries_raster(self, size: int):
        labelled = list(filter(lambda smpl: smpl.labels != [], db.get(Dataset, self.dataset_id).samples))
        feature_df = pd.DataFrame([
            sample.feature_dict() for sample in labelled
        ])
        feature_domains = {}
        for feature in feature_df.columns:
            dtype = feature_df.dtypes[feature]
            if dtype == int or dtype == float:
                feature_domains[feature] = np.array([feature_df[feature].min(), feature_df[feature].max()],
                                                    dtype)
            else:
                feature_domains[feature] = feature_df[feature].unique()
        random_sample_tmp = []
        for i in range(size):
            new_sample = {}
            for feature in feature_df.columns:
                domain = feature_domains[feature]
                if domain.dtype == int:
                    new_sample[feature] = np.random.randint(low=domain[0], high=domain[1] + 1)
                elif domain.dtype == float:
                    new_sample[feature] = np.random.uniform(low=domain[0], high=domain[1])
                else:
                    new_sample[feature] = np.random.choice(domain)
            random_sample_tmp.append(new_sample)

        return pd.DataFrame(columns=feature_df.columns, data=random_sample_tmp)

    def start(self):
        for exp in self.experiments:
            exp.start()
        self.started_flags = [True for _ in self.started_flags]

    def get_status(self) -> Status:
        """ @return
                -1 if both are finished
                -2 if no (new) data is available
                time in seconds if at least one has finished one iteration
                """
        self.assert_started()
        times = [self.poll_process(i) for i in [0, 1]]
        if not all(self.setup_completed_flags):
            return Status(code=Status.Code.IN_SETUP)
        if all(self.finished_flags):
            return Status(code=Status.Code.COMPLETED)  # experiments are finished: both results are reported
        if all(t is None for t in times):
            return Status(code=Status.Code.TRAINING)  # experiments not finished and no new time
        if self.last_reported_time is None:
            times = list(filter(lambda t: t is not None, times))
            t = max(times)
            self.last_reported_time = t, times.index(t)
            return Status(code=Status.Code.TRAINING, time=max(times))
        for i, t in enumerate(times):
            if t is not None and (t > self.last_reported_time[0] or i == self.last_reported_time[1]):
                self.last_reported_time = t, i
        return Status(code=Status.Code.TRAINING, time=self.last_reported_time[0])

    def get_metrics(self) -> Metric:
        if self.metric is not None:
            return self.metric
        self.assert_finished()
        self._poll_results_if_not_present()

        def extract_per_exp(idx: int):
            r = self.results[idx]
            assert len(r.meta_data) == len(r.metric_scores.index)
            scores: List = [MetricScoresIteration.of(row[1]) for row in r.metric_scores.iterrows()]
            return [MetricIteration(meta=r.meta_data[i], metrics=scores[i]) for i in range(len(scores))]

        self.metric = Metric(
            iterations=list(zip_unequal(
                extract_per_exp(0),
                extract_per_exp(1))),
            percentage_similar=self._percentage_similar_samples()
        )
        return self.metric

    # Methods for plot related data
    def get_learning_curve_data(self) -> pd.DataFrame:
        # convert to long form for altair
        self.assert_finished()
        self._poll_results_if_not_present()

        def gen(idx, key):
            return [(it, key, item[MetricsDFKeys.Acc]) for it, item in self.results[idx].metric_scores.iterrows()]

        rows = gen(0, "First")
        rows += gen(1, "Second")
        return pd.DataFrame(data=rows, columns=["Iteration", "Experiment", "Value"])

    def get_confidence_his_data(self) -> Tuple[List[List[float]], List[List[float]]]:
        # return
        self.assert_finished()
        self._poll_results_if_not_present()

        def gen(experiment_idx: int):
            data_over_iterations = []
            for _, row in self.results[experiment_idx].raw_predictions.iterrows():
                data_over_iterations.append(list(np.max(row)))
            return data_over_iterations

        return gen(0), gen(1)

    def get_data_map_data(self):
        self.assert_finished()
        self._poll_results_if_not_present()

        def gen(exp_idx: int):
            r = self.results[exp_idx]
            raw_predicts = r.raw_predictions
            data = []
            for smpl in raw_predicts.columns:
                confidence = raw_predicts[smpl].map(lambda x: max(x)).mean()
                variance = raw_predicts[smpl].map(lambda x: x.index(max(x))).var()
                correctness = raw_predicts[smpl].map(lambda x: x.index(max(x)) == r.correct_labelAsIdx[smpl]).mean()
                data.append({'Confidence': confidence,
                             'Variability': variance,
                             'Correctness': correctness,
                             'SampleID': smpl})
            return pd.DataFrame(data)

        return gen(0), gen(1)

    def _use_pca_for_feature_selection(self):
        dataset = db.get(Dataset, self.dataset_id)
        feature_names = dataset.feature_names

        samples_df = pd.DataFrame([
            [smpl.id] + smpl.extract_feature_list()
            for smpl in dataset.samples
            if smpl.labels != []], columns=["SampleID"] + feature_names.split(","))
        pca = PCA(n_components=2)
        transformed_samples = pca.fit_transform(X=samples_df.iloc[:, 1:])
        pca_df = pd.DataFrame(data=transformed_samples, columns=["PCA1", "PCA2"])
        pca_df["SampleID"] = samples_df["SampleID"]
        pca_df.set_index("SampleID")
        return pca_df

    def _use_names_for_feature_selection(self, name_one: str, name_two: str):
        samples: List[Sample] = db.get(Dataset, self.dataset_id).samples
        all_samples: pd.DataFrame = pd.DataFrame([
            {
                "SampleID": smpl.id,
                name_one: smpl.feature_dict()[name_one],
                name_two: smpl.feature_dict()[name_two]
            }
            for smpl in samples]
        )
        all_samples.set_index("SampleID")
        return all_samples

    def get_vector_space_data(self) -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:
        """ @return for each experiment for each iteration a data-frame with columns:
                <feature-one>, <feature-two>, SampleID, Color"""
        self.assert_finished()
        self._poll_results_if_not_present()

        two_feature_df = self._use_pca_for_feature_selection() \
            if self.config.PLOT_CONFIG.FEATURES is None \
            else self._use_names_for_feature_selection(*self.config.PLOT_CONFIG.FEATURES)

        def classify(ID, selected_ids, labeled_ids):
            return 'Selected' if ID in selected_ids \
                else 'Labeled' if ID in labeled_ids \
                else 'Unlabeled'

        def gen(exp_idx: int):
            r = self.results[exp_idx]
            labeled_ids = r.initially_labeled
            iterations = []
            for metric_data in r.meta_data:
                it_df: pd.DataFrame = two_feature_df.copy()
                selected_ids = metric_data.sample_ids
                labeled_ids += selected_ids
                it_df['Color'] = it_df['SampleID'].apply(lambda ID: classify(ID, selected_ids, labeled_ids))
                iterations.append(it_df)
            return iterations

        return gen(0), gen(1)

    def get_classification_boundary_data(self) -> ClassificationBoundariesDTO:
        self.assert_finished()
        self._poll_results_if_not_present()

        if self.config.PLOT_CONFIG.FEATURES is None:
            # ndarray with list of rows of [feature_1, feature_2]
            reduced_features = pd.DataFrame(
                PCA(n_components=2).fit_transform(self.cb_sample),
                columns=['PCA1', 'PCA2'])
        else:
            reduced_features = self.cb_sample.loc[:, self.config.PLOT_CONFIG.FEATURES]

        def for_each_iteration(iteration: pd.Series, classes):
            return pd.DataFrame(data={
                'Class': [classes[item.index(max(item))] for _, item in iteration.iteritems()],
                'Confidence': [max(item) for _, item in iteration.iteritems()]
            })

        def gen(exp_idx):
            result = self.results[exp_idx]
            assert len(result.cb_predictions.columns) == len(self.cb_sample)
            # get predicted class and confidence for pseudo samples
            iteration_list = [for_each_iteration(row, result.classes) for _, row in result.cb_predictions.iterrows()]
            return iteration_list

        return ClassificationBoundariesDTO(reduced_features, gen(0), gen(1))

    # assertions
    def assert_started(self):
        if not all(self.started_flags):
            raise ValidationError(
                f"At least one experiment was not started ({[e for e in [0, 1] if not self.started_flags[e]]})")

    def assert_finished(self):
        self.assert_started()
        if not all(self.finished_flags):  # TODO
            for exp_idx in [0, 1]:
                if self.results[exp_idx] is None:
                    self.poll_process(exp_idx)
            if not all(self.finished_flags):
                raise ValidationError(
                    f"At least one experiment is not finished ({[e for e in [0, 1] if not self.finished_flags[e]]})")

    # other
    def _percentage_similar_samples(self):
        self.assert_finished()
        self._poll_results_if_not_present()

        samples_one = [r.sample_ids for r in self.results[0].meta_data]
        samples_two = [r.sample_ids for r in self.results[1].meta_data]
        assert len(samples_one) == len(samples_two)
        similar_per_iteration = []
        for i in range(15):
            s_one = set(np.concatenate(samples_one[:i + 1]))
            s_two = set(np.concatenate(samples_two[:i + 1]))
            similar_samples = len(s_one.intersection(s_two))
            similar_percentage = similar_samples / len(s_one.union(s_two))
            similar_per_iteration.append(similar_percentage)
        return similar_per_iteration

    def _poll_results_if_not_present(self):
        self.assert_finished()
        if all(r is not None for r in self.results):
            return
        for exp_idx in [0, 1]:
            if self.results[exp_idx] is None:
                self.poll_process(exp_idx)

    def poll_process(self, exp_idx: int) -> Optional[float]:
        """
        @param exp_idx the queue of experiment one or two
        @return If the result was not send -> return the last send time
                If no new time was reported or is finished return None
        """
        if exp_idx not in [0, 1]:
            raise ValidationError(f"index of experiment was neither 0 nor 1: {exp_idx}")
        if self.finished_flags[exp_idx]:
            return None
        last_time = None
        queue = self.queues[exp_idx]
        while not queue.empty():
            event = queue.get_nowait()
            if event['Type'] == EventType.INFO:
                last_time = event['Value']
            elif event['Type'] == EventType.SETUP_COMPLETED:
                self.setup_completed_flags[exp_idx] = True
            elif event['Type'] == EventType.RESULT:
                self.results[exp_idx] = event['Value']
                self.experiments[exp_idx].join()
                self.finished_flags[exp_idx] = True
                return None

        return last_time

    def terminate(self):
        logger.info(f"Terminating experiment with ID: {getattr(self, 'dataset_id', 'Unknown')}")
        if not hasattr(self, 'finished_flags') or hasattr(self, 'experiments'):
            return
        for exp_ind, finished in enumerate(self.finished_flags):
            if not finished:
                self.experiments[exp_ind].kill()
        if not hasattr(self, 'queues'):
            return
        for q in self.queues:
            q.close()

    def __del__(self):
        self.terminate()
