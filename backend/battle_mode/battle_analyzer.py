from __future__ import annotations

from typing import Tuple, Optional, List

import numpy as np
import pandas as pd
from altair import UrlData, CsvDataFormat
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
    VectorSpaceDTO,
    MetricScoresIteration,
    MetricIteration,
)
from ..utils import zip_unequal


class BattleAnalyzer:
    def __init__(
        self,
        experiment_id: int,
        dataset_id: int,
        config: ALBattleConfig,
        cb_sample: pd.DataFrame,
        result_one: ExperimentResults,
        result_two: ExperimentResults,
    ):
        if (
            config is None
            or cb_sample is None
            or result_one is None
            or result_two is None
        ):
            raise ValueError("At least one parameter was null.")
        self.experiment_id: int = experiment_id
        self.dataset_id: int = dataset_id
        self.config: ALBattleConfig = config
        # row = randomly generated Sample, columns = feature-names [2]
        self.cb_sample: pd.DataFrame = cb_sample
        self.results: Tuple[ExperimentResults, ExperimentResults] = (
            result_one,
            result_two,
        )
        self.metric: Optional[Metric] = None
        # cache plot data
        self.vector_space_data: Optional[
            Tuple[List[pd.DataFrame], List[pd.DataFrame]]
        ] = None
        self.classification_boundaries_data: Optional[
            Tuple[List[pd.DataFrame], List[pd.DataFrame]]
        ] = None
        # list-entry = iteration, rows = Samples, columns = metric-scores
        self.data_maps: Optional[Tuple[List[pd.DataFrame], List[pd.DataFrame]]] = None

    # Methods for plot related data
    def get_learning_curve_data(self) -> pd.DataFrame:
        # convert to long form for altair

        def gen(idx, key):
            return [
                (it, key, item[MetricsDFKeys.Acc])
                for it, item in self.results[idx].metric_scores.iterrows()
            ]

        #  rows = gen(0, "First")
        #  rows += gen(1, "Second")

        rows = gen(0, self.config.exp_configs[0].QUERY_STRATEGY)
        rows += gen(1, self.config.exp_configs[1].QUERY_STRATEGY)

        return pd.DataFrame(data=rows, columns=["Iteration", "Experiment", "Value"])

    def get_confidence_his_data(self) -> Tuple[List[List[float]], List[List[float]]]:
        def gen(experiment_idx: int):
            data_over_iterations = []
            for _, row in self.results[experiment_idx].raw_predictions.iterrows():
                data_over_iterations.append(list(row.map(lambda cell: max(cell))))
            return data_over_iterations

        return gen(0), gen(1)

    def get_data_map_data(self) -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:
        def for_each_iteration(
            iteration: int, raw_predictions: pd.DataFrame, correct_label_as_idx
        ):
            # use the last 10 iterations as input
            first_iteration = max(0, iteration - 10)
            # include current iteration
            reduced_frame = raw_predictions.iloc[first_iteration : (iteration + 1), :]
            data = []
            for smpl in reduced_frame.columns:
                confidence = reduced_frame[smpl].map(lambda x: max(x)).mean()
                variance = reduced_frame[smpl].map(lambda x: x.index(max(x))).var()
                variance = (
                    0.0 if np.isnan(variance) else variance
                )  # if only one iteration var() returns nan
                correctness = (
                    reduced_frame[smpl]
                    .map(lambda x: x.index(max(x)) == correct_label_as_idx[smpl])
                    .mean()
                )
                data.append(
                    {
                        "Confidence": confidence,
                        "Variability": variance,
                        "Correctness": correctness,
                        "SampleID": smpl,
                    }
                )

            return pd.DataFrame(data)

        def gen(exp_idx: int) -> List[pd.DataFrame]:
            r = self.results[exp_idx]
            raw_predictions: pd.DataFrame = r.raw_predictions
            return [
                for_each_iteration(iteration, raw_predictions, r.correct_label_as_idx)
                for iteration in raw_predictions.index
            ]

        return gen(0), gen(1)

    def get_data_map_description(self, base_url: str) -> DataMapsDTO:
        data = self.get_data_map_data()
        descriptions = BattleAnalyzer._describe_based_on_size(
            data, base_url, "data-map"
        )
        return DataMapsDTO(
            exp_one_iterations=descriptions[0], exp_two_iterations=descriptions[1]
        )

    def _use_pca_for_feature_selection(self, exclude: List[int]):
        dataset = db.get(Dataset, self.dataset_id)
        feature_names = dataset.feature_names
        samples = [
            s
            for s in db.query(Sample)
            .filter(Sample.dataset_id == self.dataset_id)
            .filter(Sample.id.not_in(exclude))
            .all()
            if s.labels != []
        ]

        samples_df = pd.DataFrame(
            [[smpl.id] + smpl.extract_feature_list() for smpl in samples],
            columns=["SampleID"] + feature_names.split(","),
        )
        pca = PCA(n_components=2)
        transformed_samples = pca.fit_transform(X=samples_df.iloc[:, 1:])
        pca_df = pd.DataFrame(data=transformed_samples, columns=["PCA1", "PCA2"])
        pca_df["SampleID"] = samples_df["SampleID"]
        pca_df.set_index("SampleID")
        return pca_df

    def _use_names_for_feature_selection(
        self, name_one: str, name_two: str, exclude: List[int]
    ):
        samples = [
            s
            for s in db.query(Sample)
            .filter(Sample.dataset_id == self.dataset_id)
            .filter(Sample.id.not_in(exclude))
            .all()
            if s.labels != []
        ]
        all_samples: pd.DataFrame = pd.DataFrame(
            [
                {
                    "SampleID": smpl.id,
                    name_one: smpl.feature_dict()[name_one],
                    name_two: smpl.feature_dict()[name_two],
                }
                for smpl in samples
            ]
        )
        all_samples.set_index("SampleID")
        return all_samples

    def get_vector_space_data(self) -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:
        """@return for each experiment for each iteration a data-frame with columns:
        <feature-one>, <feature-two>, SampleID, Color"""
        if self.vector_space_data is not None:
            return self.vector_space_data

        def gen(exp_idx: int):
            r = self.results[exp_idx]
            # reduced_features_df['SampleID'] == all training sample
            test_sample = list(map(lambda id_: int(id_), r.raw_predictions.columns))
            reduced_features_df = (
                self._use_pca_for_feature_selection(exclude=test_sample)
                if self.config.PLOT_CONFIG.FEATURES is None
                else self._use_names_for_feature_selection(
                    *self.config.PLOT_CONFIG.FEATURES, exclude=test_sample
                )
            )

            labeled_ids = r.initially_labeled.copy()
            iterations = []
            for meta_data in r.meta_data:
                it_df: pd.DataFrame = reduced_features_df.copy()
                selected_ids = meta_data.sample_ids
                labeled_ids += selected_ids
                it_df["Color"] = it_df["SampleID"].apply(
                    lambda ID: classify(ID, selected_ids, labeled_ids)
                )
                iterations.append(it_df)
            return iterations

        def classify(ID, selected_ids, labeled_ids):
            return (
                "Selected"
                if ID in selected_ids
                else ("Labeled" if ID in labeled_ids else "Unlabeled")
            )

        self.vector_space_data = gen(0), gen(1)
        return self.vector_space_data

    def get_vector_space_data_description(self, base_url: str) -> VectorSpaceDTO:
        data = self.get_vector_space_data()
        descriptions = BattleAnalyzer._describe_based_on_size(
            data, base_url, "vector-space"
        )
        f1, f2 = [f for f in data[0][0].columns if f not in ["Color", "SampleID"]]
        return VectorSpaceDTO(
            exp_one_iterations=descriptions[0],
            exp_two_iterations=descriptions[1],
            feature_one_name=f1,
            feature_two_name=f2,
        )

    def get_classification_boundary_data(
        self,
    ) -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:

        if self.classification_boundaries_data is not None:
            return self.classification_boundaries_data

        if self.config.PLOT_CONFIG.FEATURES is None:
            # ndarray with list of rows of [feature_1, feature_2]
            reduced_features = pd.DataFrame(
                PCA(n_components=2).fit_transform(self.cb_sample),
                columns=["PCA1", "PCA2"],
            )
        else:
            reduced_features = self.cb_sample.loc[:, self.config.PLOT_CONFIG.FEATURES]

        def for_each_iteration(iteration: pd.Series, classes: List[str]):
            iter_pf = pd.DataFrame(
                data={
                    "Class": [
                        classes[confidence_scores.index(max(confidence_scores))]
                        for _, confidence_scores in iteration.iteritems()
                    ],
                    "Confidence": [max(item) for _, item in iteration.iteritems()],
                }
            )
            return pd.merge(
                reduced_features, iter_pf, left_index=True, right_index=True
            )

        def gen(exp_idx):
            result = self.results[exp_idx]
            assert len(result.cb_predictions.columns) == len(self.cb_sample)
            # get predicted class and confidence for pseudo samples
            iteration_list = [
                for_each_iteration(row, result.classes)
                for _, row in result.cb_predictions.iterrows()
            ]
            return iteration_list

        self.classification_boundaries_data = gen(0), gen(1)
        return self.classification_boundaries_data

    def get_classification_boundaries_description(
        self, base_url: str
    ) -> ClassificationBoundariesDTO:
        data = self.get_classification_boundary_data()
        descriptions = BattleAnalyzer._describe_based_on_size(
            data, base_url, "classification-boundaries"
        )
        f1, f2 = [f for f in data[0][0].columns if f not in ["Confidence", "Class"]]
        return ClassificationBoundariesDTO(
            exp_one_iterations=descriptions[0],
            exp_two_iterations=descriptions[1],
            x_bins=self.config.PLOT_CONFIG.CLASSIFICATION_BOUNDARIES.MAX_X_BINS,
            y_bins=self.config.PLOT_CONFIG.CLASSIFICATION_BOUNDARIES.MAX_Y_BINS,
            feature_one_name=f1,
            feature_two_name=f2,
        )

    def get_metrics(self) -> Metric:
        if self.metric is not None:
            return self.metric

        def extract_per_exp(idx: int):
            r = self.results[idx]
            assert len(r.meta_data) == len(r.metric_scores.index)
            scores: List = [
                MetricScoresIteration.of(row[1]) for row in r.metric_scores.iterrows()
            ]
            return [
                MetricIteration(meta=r.meta_data[i], metrics=scores[i])
                for i in range(len(scores))
            ]

        self.metric = Metric(
            iterations=list(zip_unequal(extract_per_exp(0), extract_per_exp(1))),
            percentage_similar=self._percentage_similar_samples(),
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
            s_one = set(np.concatenate(samples_one[: i + 1]))
            s_two = set(np.concatenate(samples_two[: i + 1]))
            similar_samples = len(s_one.intersection(s_two))
            similar_percentage = similar_samples / len(s_one.union(s_two))
            similar_per_iteration.append(similar_percentage)
        return similar_per_iteration

    @staticmethod
    def _describe_based_on_size(
        data: Tuple[List[pd.DataFrame], List[pd.DataFrame]],
        base_url: str,
        url_infix: str,
    ):
        iterations = len(data[0])
        if any(len(frame) > 5000 for frame in data[0]) or any(
            len(frame) > 5000 for frame in data[1]
        ):
            descriptions = BattleAnalyzer._describe_by_url(
                base_url, url_infix, iterations
            )
        else:
            descriptions = data
        return descriptions

    @staticmethod
    def _describe_by_url(
        base_url: str, url_infix: str, iterations: int
    ) -> List[List[UrlData]]:
        descriptions = []
        for exp_idx in [0, 1]:
            per_experiment = []
            for i in range(iterations):
                url = base_url + f"/{url_infix}/{exp_idx}/{i}"
                per_experiment.append(
                    UrlData(
                        url=url,
                        format=CsvDataFormat(type="csv"),
                        name=url_infix + "_iteration",
                    )
                )
            descriptions.append(per_experiment)
        return descriptions
