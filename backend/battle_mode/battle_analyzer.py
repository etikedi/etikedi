from __future__ import annotations

from typing import Tuple, Optional, List

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from ..config import db
from ..models import (
    ALBattleConfig,
    ExperimentResults,
    Metric,
    MetricsDFKeys,
    DataMapsDTO,
    Dataset,
    Sample,
    ClassificationBoundariesDTO,
    MetricScoresIteration,
    MetricIteration)
from ..utils import zip_unequal


class BattleAnalyzer:

    def __init__(
            self,
            experiment_id: int,
            dataset_id: int,
            config: ALBattleConfig,
            cb_sample: pd.DataFrame,
            result_one: ExperimentResults,
            result_two: ExperimentResults):
        if config is None or cb_sample is None or result_one is None or result_two is None:
            raise ValueError("At least one parameter was null.")
        self.experiment_id: int = experiment_id
        self.dataset_id: int = dataset_id
        self.config: ALBattleConfig = config
        self.cb_sample: pd.DataFrame = cb_sample
        self.results: Tuple[ExperimentResults, ExperimentResults] = (result_one, result_two)
        self.metric: Optional[Metric] = None

    # Methods for plot related data
    def get_learning_curve_data(self) -> pd.DataFrame:
        # convert to long form for altair

        def gen(idx, key):
            return [(it, key, item[MetricsDFKeys.Acc]) for it, item in self.results[idx].metric_scores.iterrows()]

        rows = gen(0, "First")
        rows += gen(1, "Second")
        return pd.DataFrame(data=rows, columns=["Iteration", "Experiment", "Value"])

    def get_confidence_his_data(self) -> Tuple[List[List[float]], List[List[float]]]:

        def gen(experiment_idx: int):
            data_over_iterations = []
            for _, row in self.results[experiment_idx].raw_predictions.iterrows():
                data_over_iterations.append(list(row.map(lambda cell: max(cell))))
            return data_over_iterations

        return gen(0), gen(1)

    def get_data_map_data(self) -> DataMapsDTO:

        def for_each_iteration(iteration: int, raw_predictions: pd.DataFrame, correct_label_as_idx):
            # use the last 10 iterations as input
            first_iteration = max(0, iteration - 10)
            # include current iteration
            reduced_frame = raw_predictions.iloc[first_iteration:(iteration + 1), :]
            data = []
            for smpl in reduced_frame.columns:
                confidence = reduced_frame[smpl].map(lambda x: max(x)).mean()
                variance = reduced_frame[smpl].map(lambda x: x.index(max(x))).var()
                correctness = reduced_frame[smpl].map(lambda x: x.index(max(x)) == correct_label_as_idx[smpl]).mean()
                data.append({'Confidence': confidence,
                             'Variability': variance,
                             'Correctness': correctness,
                             'SampleID': smpl})
            return pd.DataFrame(data)

        def gen(exp_idx: int) -> List[pd.DataFrame]:
            r = self.results[exp_idx]
            raw_predictions: pd.DataFrame = r.raw_predictions
            return [for_each_iteration(iteration, raw_predictions, r.correct_label_as_idx)
                    for iteration in raw_predictions.index]

        return DataMapsDTO(exp_one_data=gen(0), exp_two_data=gen(1))

    def _use_pca_for_feature_selection(self, sample_ids: List[int]):
        dataset = db.get(Dataset, self.dataset_id)
        feature_names = dataset.feature_names
        samples = db.query(Sample).filter(Sample.id.in_(sample_ids)).all()

        samples_df = pd.DataFrame([
            [smpl.id] + smpl.extract_feature_list()
            for smpl in samples],
            columns=["SampleID"] + feature_names.split(","))
        pca = PCA(n_components=2)
        transformed_samples = pca.fit_transform(X=samples_df.iloc[:, 1:])
        pca_df = pd.DataFrame(data=transformed_samples, columns=["PCA1", "PCA2"])
        pca_df["SampleID"] = samples_df["SampleID"]
        pca_df.set_index("SampleID")
        return pca_df

    @staticmethod
    def _use_names_for_feature_selection(name_one: str, name_two: str, sample_ids: List[int]):
        samples: List[Sample] = db.query(Sample).filter(Sample.id.in_(sample_ids)).all()
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
        # both experiments should have the same fully labeled pool of samples so 0 or 1 does not make a difference
        # int(s) because sqlalchemy does not accept np.int64 for id checks
        sample_ids = list(map(lambda s: int(s), np.concatenate([m.sample_ids for m in self.results[0].meta_data]))) + \
                     self.results[0].initially_labeled
        reduced_features_df = self._use_pca_for_feature_selection(sample_ids) \
            if self.config.PLOT_CONFIG.FEATURES is None \
            else self._use_names_for_feature_selection(*self.config.PLOT_CONFIG.FEATURES, sample_ids=sample_ids)

        def classify(ID, selected_ids, labeled_ids):
            return 'Selected' if ID in selected_ids \
                else ('Labeled' if ID in labeled_ids
                      else 'Unlabeled')

        def gen(exp_idx: int):
            r = self.results[exp_idx]
            labeled_ids = r.initially_labeled.copy()
            iterations = []
            for meta_data in r.meta_data:
                it_df: pd.DataFrame = reduced_features_df.copy()
                selected_ids = meta_data.sample_ids
                labeled_ids += selected_ids
                it_df['Color'] = it_df['SampleID'].apply(lambda ID: classify(ID, selected_ids, labeled_ids))
                iterations.append(it_df)
            return iterations

        return gen(0), gen(1)

    def get_classification_boundary_data(self) -> ClassificationBoundariesDTO:

        if self.config.PLOT_CONFIG.FEATURES is None:
            # ndarray with list of rows of [feature_1, feature_2]
            reduced_features = pd.DataFrame(
                PCA(n_components=2).fit_transform(self.cb_sample),
                columns=['PCA1', 'PCA2'])
        else:
            reduced_features = self.cb_sample.loc[:, self.config.PLOT_CONFIG.FEATURES]

        def for_each_iteration(iteration: pd.Series, classes: List[str]):
            return pd.DataFrame(data={
                'Class': [classes[confidence_scores.index(max(confidence_scores))] for _, confidence_scores in
                          iteration.iteritems()],
                'Confidence': [max(item) for _, item in iteration.iteritems()]
            })

        def gen(exp_idx):
            result = self.results[exp_idx]
            assert len(result.cb_predictions.columns) == len(self.cb_sample)
            # get predicted class and confidence for pseudo samples
            iteration_list = [for_each_iteration(row, result.classes) for _, row in result.cb_predictions.iterrows()]
            return iteration_list

        return ClassificationBoundariesDTO(
            reduced_features=reduced_features,
            exp_one_iterations=gen(0),
            exp_two_iterations=gen(1),
            x_bins=self.config.PLOT_CONFIG.CLASSIFICATION_BOUNDARIES.MAX_X_BINS,
            y_bins=self.config.PLOT_CONFIG.CLASSIFICATION_BOUNDARIES.MAX_Y_BINS)

    def get_metrics(self) -> Metric:
        if self.metric is not None:
            return self.metric

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

    def _percentage_similar_samples(self):
        """
        In each experiment n sample get labeled, which is determined by the al-query.
        For each iteration it: this method compares the similarity of those n sample for each iteration until it.
        100 % would mean that the pool of labeled samples is the same for both experiments in iteration it,
        which would also be true if the samples were picked in different iterations (as long as before it).
        Returns: The similarity in percent for each iteration.
        """
        samples_one = [r.sample_ids for r in self.results[0].meta_data]
        samples_two = [r.sample_ids for r in self.results[1].meta_data]
        assert len(samples_one) == len(samples_two)
        similar_per_iteration = []
        for i in range(len(samples_one)):
            s_one = set(np.concatenate(samples_one[:i + 1]))
            s_two = set(np.concatenate(samples_two[:i + 1]))
            similar_samples = len(s_one.intersection(s_two))
            similar_percentage = similar_samples / len(s_one.union(s_two))
            similar_per_iteration.append(similar_percentage)
        return similar_per_iteration
