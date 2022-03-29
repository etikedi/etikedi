from __future__ import annotations  # necessary in order to use ExperimentManager as type hint

import time
from multiprocessing import Process
from multiprocessing import Queue
from typing import List, Dict

import numpy as np
import pandas as pd
from alipy.data_manipulate import split
from alipy.experiment import StoppingCriteria, StateIO, State
from alipy.index import IndexCollection
from math import ceil
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, auc, pairwise_distances

from ..config import db
from ..models import (
    ALModel,
    ALBattleConfig,
    AlExperimentConfig,
    QueryStrategyAbstraction,
    MetaData,
    MetricsDFKeys,
    EventType,
    MapKeys,
    Dataset,
    StoppingCriteriaOption)
from ..utils import timeit


class ExperimentResults:
    def __init__(self,
                 raw_predictions: pd.DataFrame,
                 initially_labeled,
                 cb_predictions: pd.DataFrame = None,
                 metric_scores: pd.DataFrame = None,
                 correct_label_as_idx: Dict[int, int] = None,
                 meta_data: List[MetaData] = None,
                 classes=None):
        self.metric_scores: pd.DataFrame = pd.DataFrame(columns=[metric_key for metric_key in MetricsDFKeys]) \
            if metric_scores is None else metric_scores
        self.meta_data: List[MetaData] = [] if meta_data is None else meta_data
        self.classes: List[str] = classes if classes is not None else []
        self.raw_predictions: pd.DataFrame = raw_predictions
        self.correct_label_as_idx: Dict[int, int] = dict() if correct_label_as_idx is None else correct_label_as_idx
        self.initially_labeled: List[int] = initially_labeled  # all initially labeled samples as SampleIDs
        # 3D data-frame: row = iteration, column = sample, value = tuple of confidence per class
        self.cb_predictions: pd.DataFrame = pd.DataFrame() if cb_predictions is None else cb_predictions


@timeit
def _transform_dataset(dataset_id: int):
    dataset: Dataset = db.get(Dataset, dataset_id)
    feature_names: List[str] = dataset.feature_names.split(",")
    frame = pd.DataFrame(data=
                         [{f_name: f for (f_name, f) in
                           zip(feature_names + ['LABEL', "DB_ID"],
                               sample.extract_feature_list() + [sample.labels[0].name, sample.id])}
                          for sample in dataset.samples if sample.labels != []])
    # TODO some models / query_strategies need number based label
    # labels = frame['LABEL'].unique()
    # label2Int = {label: i for i, label in enumerate(labels)}
    # frame['Label'] = frame['LABEL'].map(label2Int)
    # int2Label: dict[int, str] = {i: label for label, i in label2Int.items()}
    return frame


class ALExperimentProcess(Process):
    class RemainingTimeEstimate:
        def __init__(self, criteria: StoppingCriteriaOption, experiment: ALExperimentProcess):
            self._start_time = None
            self._criteria: StoppingCriteriaOption = criteria
            self._criteria_value = experiment.battle_config.STOPPING_CRITERIA_VALUE
            self._times = []  # iteration : measured_time
            self._total_iterations: int = 0
            if criteria == StoppingCriteriaOption.PERCENT_OF_UNLABEL:
                percentage_as_absolute: int = ceil(len(experiment.unlab_ind) * float(self._criteria_value))
                self._total_iterations = ceil(percentage_as_absolute / experiment.batch_size)
            elif criteria == StoppingCriteriaOption.NUM_OF_QUERIES:
                self._total_iterations = int(self._criteria_value)
            # TODO estimate time for cost limit
            if criteria == StoppingCriteriaOption.ALL_LABELED or criteria == StoppingCriteriaOption.COST_LIMIT:
                self._total_iterations = ceil(len(experiment.unlab_ind) / experiment.batch_size)

        def remaining_time(self, last_training_time: float) -> float:
            """
            Assuming this method is called every iteration once.
            @param last_training_time: time for model.fit() in ns
            @return: estimated remaining time in seconds
            """
            self._times.append(last_training_time)
            it = len(self._times)
            if self._criteria == StoppingCriteriaOption.CPU_TIME:
                if self._start_time is None:
                    raise ValueError("start_timer() was not called")
                return max(self._criteria_value - (time.perf_counter_ns() - self._start_time), 0) * 1e-9

            incr = sum(self._times[i + 1] - self._times[i] for i in range(it - 1)) / max(it - 1, 1)
            result = sum([last_training_time + incr * i for i in range(self._total_iterations - it)])
            if result < 0.0:
                print(f"[Warning] Remaining time is negative: {result}")
            return result * 1e-9  # convert ns to seconds

        def start_timer(self):
            if self._criteria != StoppingCriteriaOption.CPU_TIME:
                raise ValueError(f"This method is only relevant if criteria is : {StoppingCriteriaOption.CPU_TIME}")
            # not one to one what alipy is using but necessary for estimation
            self._start_time = time.perf_counter_ns()

    def __init__(self, exp_id: int, dataset_id: int, battle_config: ALBattleConfig, queue: Queue,
                 cb_sample: pd.DataFrame):
        """
         The dataset is first filtered by hasLabel and split into training and test.
         The test-set is further split into initially_unlabeled and initially_labeled.
         As long as the stopping criteria is not met the main training loop is executed.
         The loop contains of 4 steps:
          1. Get to_be_labeled samples from the al_strategy,
          2. train model on new available data,
          3. test model,
          4. save current iteration in history.
        """
        super().__init__()
        self.cb_sample: pd.DataFrame = cb_sample
        self.cb_sample_as_numpy: np.ndarray = cb_sample.to_numpy()
        self.cb_sample_predictions = pd.DataFrame()
        self.exp_id = exp_id
        self.battle_config: ALBattleConfig = battle_config
        self.exp_config: AlExperimentConfig = battle_config.exp_configs[exp_id]
        self.queue = queue
        model_class = self.exp_config.AL_MODEL.get_class()
        self.model = model_class() if self.exp_config.AL_MODEL != ALModel.SVC else model_class(probability=True)
        self.stopping_criteria = StoppingCriteria(stopping_criteria=battle_config.STOPPING_CRITERIA.get()) \
            if (battle_config.STOPPING_CRITERIA_VALUE is None) \
            else StoppingCriteria(battle_config.STOPPING_CRITERIA.get(), battle_config.STOPPING_CRITERIA_VALUE)
        self.batch_size = battle_config.BATCH_SIZE
        self.dataset_id = dataset_id
        # move time intensive data operations outside __init__
        self.all_training_samples = None
        self.all_training_labels = None
        self.idx2IDTrain = None
        self.idx2IDTest = None
        self.unlab_ind = None
        self.label_ind = None
        self.label_ind = None
        self.prediction_history = None
        self.X_test = None
        self.y_test = None
        self.state_saver = None
        self.rte = None  # RemainingTimeEstimate instance predicting the remaining time

    @timeit
    def _setup(self):
        d_frame: pd.DataFrame = _transform_dataset(self.dataset_id)
        print(f"[{self.exp_id}] Loaded dataset")
        labeled_set = d_frame[d_frame['LABEL'].notnull()]
        all_labeled_samples = labeled_set.drop(labels=['LABEL', 'DB_ID'], axis='columns')
        labels = labeled_set['LABEL']

        self.idx2Label = {idx: label for idx, label in enumerate(set(labels))}

        train_idx, test_idx, label_idx, unlabel_idx = split(
            X=all_labeled_samples,
            y=labels.to_numpy(),
            test_ratio=0.3,
            split_count=1,
            all_class=True,
            saving_path=None)
        train_idx = train_idx[0]
        test_idx = test_idx[0]
        label_idx = label_idx[0]
        unlabel_idx = unlabel_idx[0]
        self.all_training_samples = all_labeled_samples.iloc[train_idx, :]
        self.all_training_labels = labels.iloc[train_idx]

        # al_strategy.select() only accepts idx from 0 to size of training data
        adjusted_idx_map = {idx: new_idx for new_idx, idx in enumerate(train_idx)}
        self.all_training_samples.reset_index(drop=True, inplace=True)

        self.idx2IDTrain = {new_idx: d_frame.iloc[idx]['DB_ID'] for new_idx, idx in enumerate(train_idx)}
        self.idx2IDTest = {idx: d_frame.iloc[idx]['DB_ID'] for idx in test_idx}

        # initiate configurable experiment setting
        if hasattr(self.exp_config.QUERY_STRATEGY_CONFIG, 'train_idx'):
            self.exp_config.QUERY_STRATEGY_CONFIG.train_idx = list(
                map(lambda old_idx: adjusted_idx_map[old_idx], train_idx))
        self.al_strategy = QueryStrategyAbstraction.build(qs_type=self.exp_config.QUERY_STRATEGY,
                                                          X=self.all_training_samples.to_numpy(),
                                                          y=self.all_training_labels.to_numpy(),
                                                          config=self.exp_config.QUERY_STRATEGY_CONFIG)

        # Indexes of your unlabeled set for querying
        self.unlab_ind = IndexCollection([adjusted_idx_map[idx] for idx in unlabel_idx])
        # Indexes of your labeled set
        self.label_ind = IndexCollection([adjusted_idx_map[idx] for idx in label_idx])

        self.X_test = all_labeled_samples.iloc[test_idx, :].to_numpy()
        self.y_test = labels.iloc[test_idx]
        self.state_saver: StateIO = StateIO(round=0, train_idx=train_idx, test_idx=test_idx,
                                            init_U=self.unlab_ind.index, init_L=self.label_ind.index,
                                            verbose=False)
        self.rte = ALExperimentProcess.RemainingTimeEstimate(self.battle_config.STOPPING_CRITERIA, self)

    def run(self, verbose=0):
        # initial training
        self._setup()
        self.queue.put({'Type': EventType.SETUP_COMPLETED, 'Value': True}, False)
        self._train(verbose)
        self.queue.put({'Type': EventType.RESULT, 'Value': self.get_result()}, False)
        print(f"[{self.exp_id}] Process finished ")

    def _train(self, verbose):
        self.model.fit(*self.get_training_data())
        # test data does not change: has original index equal to all_labeled_samples

        iteration = 1
        predictions = []
        cb_sample_predictions = []
        if self.battle_config.STOPPING_CRITERIA == StoppingCriteriaOption.CPU_TIME:
            self.stopping_criteria.reset()  # reset cpu start time 
            self.rte.start_timer()
        starting_time = time.time_ns()
        while not self.stopping_criteria.is_stop():
            # query al_strategy for next samples
            selected_ind_list = self.al_strategy.select(label_index=self.label_ind,
                                                        unlabel_index=self.unlab_ind,
                                                        model=self.model,
                                                        batch_size=self.batch_size)
            self.label_ind.update(selected_ind_list)
            self.unlab_ind.difference_update(selected_ind_list)

            # train and test model
            start = time.time_ns()
            try:
                self.model.fit(*self.get_training_data())
            except Exception as e:
                print(e)
                return
            finally:
                stop = time.time_ns()
            diff_time = stop - start
            estimation = self.rte.remaining_time(diff_time)
            if iteration > 2:  # estimation not precise enough
                self.queue.put({'Type': EventType.INFO, 'Value': estimation}, False)
                if verbose > 0:
                    print(f"[{self.exp_id}] estimation: {estimation}")
            pred_proba = self.model.predict_proba(self.X_test)
            y_pred = _predicted_class(self.model, pred_proba)
            perf = accuracy_score(y_true=self.y_test.to_list(), y_pred=y_pred)
            state = State(select_index=selected_ind_list, performance=perf)
            state.add_element(key=MapKeys.TIME, value=round(diff_time * 1e-9, 4))
            state.add_element(key=MapKeys.PERC_LABELED,
                              value=len(self.label_ind) / (len(self.unlab_ind) + len(self.label_ind)))
            self.state_saver.add_state(state)
            if verbose > 0:
                print(f"[{self.exp_id}] Training took: {diff_time}ns")
                print(f"[{self.exp_id}] Performance: {perf}")
                print(f"[{self.exp_id}] #Labeled: {len(self.label_ind.index)}")

            # add current iteration to history
            predictions.append(
                {self.idx2IDTest[x]: pred for (x, pred) in zip(self.state_saver.test_idx, map(tuple, pred_proba))}
            )
            # classify the random sample used for classification boundaries
            cb_sample_predictions.append(list(map(tuple, self.model.predict_proba(self.cb_sample_as_numpy))))

            iteration += 1
            # update stopping_criteria
            self.stopping_criteria.update_information(self.state_saver)

        print(f"[{self.exp_id}] Stopped after {iteration} iterations")
        print(f"[{self.exp_id}] Training took {round((time.time_ns() - starting_time) * 1e-9, 4)} seconds")
        self.prediction_history = pd.DataFrame(predictions)
        self.cb_sample_predictions = pd.DataFrame(cb_sample_predictions)

    def get_training_data(self):
        return (
            self.all_training_samples.iloc[self.label_ind.index].to_numpy(),
            self.all_training_labels.iloc[self.label_ind.index].to_numpy())

    def get_result(self) -> ExperimentResults:
        # pandas dataframe: every column is one sample, every row is one prediction
        # every cell is a tuple of (predicted_label, certainty)
        assert len(self.state_saver) == len(self.prediction_history)
        result = ExperimentResults(
            raw_predictions=self.prediction_history,
            classes=self.model.classes_,
            initially_labeled=[self.idx2IDTrain[idx] for idx in self.state_saver.init_L]
        )
        result.cb_predictions = self.cb_sample_predictions
        result.correct_label_as_idx = {self.idx2IDTest[idx]: self.model.classes_.tolist().index(label_str)
                                       for idx, label_str in self.y_test.items()}
        result.metric_scores = self._calc_metrics_scores()
        result.meta_data = self._convert_states_data()

        return result

    def _calc_metrics_scores(self) -> pd.DataFrame:
        # Calculate Acc, F1, Recall, Precision
        metrics_tmp = []
        for idx, row in self.prediction_history.iterrows():
            y_pred: List = list(map(lambda probas: self.model.classes_[probas.index(max(probas))], row))
            y_truth: List = self.y_test.to_list()
            assert len(y_pred) == len(y_truth)
            acc = accuracy_score(y_truth, y_pred=y_pred)
            f1 = f1_score(y_truth, y_pred, average='macro', zero_division=0)
            recall = recall_score(y_truth, y_pred, average='macro', zero_division=0)
            precision = precision_score(y_truth, y_pred, average='macro', zero_division=0)
            metrics_tmp.append({
                MetricsDFKeys.Acc: acc,
                MetricsDFKeys.F1: f1,
                MetricsDFKeys.Recall: recall,
                MetricsDFKeys.Precision: precision
            })

        metric_scores = pd.DataFrame(metrics_tmp)
        # Calculate F1-AUC
        metric_scores[MetricsDFKeys.F1_AUC] = 0
        for idx in metric_scores.index:
            # idx +1 because current iteration should be included in calculation
            # auc(...) / idx in order to normalize the area under the curve
            metric_scores[MetricsDFKeys.F1_AUC][idx] = 0 if idx == 0 \
                else auc(list(range(idx + 1)), metric_scores[MetricsDFKeys.F1].iloc[:idx + 1]) / idx
        metric_scores[MetricsDFKeys.AvgDistanceLabeled] = self._calc_average_distance(labeled=True)
        metric_scores[MetricsDFKeys.AvgDistanceUnLabeled] = self._calc_average_distance(labeled=False)
        return metric_scores

    def _calc_average_distance(self, labeled: bool = True) -> List[float]:
        # if labeled continuously add all new labeled samples
        # else continuously remove the newly labeled samples
        initial = self.state_saver.init_L if labeled else self.state_saver.init_U
        # 2D array of samples, where each sample is a vector of all features
        selected_until_now = self.all_training_samples.iloc[initial].to_numpy()
        selected_idx_until_now = initial  # only kept for !labeled
        avg_dist: List[float] = []
        for _, state in enumerate(self.state_saver):
            selected_idx = state.get_value(MapKeys.SAMPLES)  # list of indices
            # same shape as selected_until_now
            selected = self.all_training_samples.iloc[selected_idx, :].to_numpy()
            if len(selected.shape) == 1:
                selected = selected.reshape(1, -1)
            avg_dist_iter = np.sum(
                pairwise_distances(
                    selected_until_now,
                    selected,
                    metric='euclidean'
                ),
                axis=(0, 1)
            )
            # normalize by the amount of labeled samples and the amount of queries we sampled
            normalized = avg_dist_iter / (len(selected_until_now) * len(selected))
            avg_dist.append(normalized)
            if not labeled:
                selected_idx_until_now = [idx for idx in selected_idx_until_now if idx not in selected_idx]
            selected_until_now = np.vstack([selected_until_now, selected]) if labeled \
                else self.all_training_samples.iloc[selected_idx_until_now]
        return avg_dist

    def _convert_states_data(self):
        state_data = []
        for idx, state in enumerate(self.state_saver):
            # transform index of samples back to id in database
            selected_samples = [self.idx2IDTrain[i] for i in state.get_value(MapKeys.SAMPLES)]
            metric_dp: MetaData = MetaData(time=state.get_value(MapKeys.TIME),
                                           percentage_labeled=state.get_value(MapKeys.PERC_LABELED),
                                           sample_ids=selected_samples)
            state_data.append(metric_dp)
        return state_data


def _predicted_class(model, pred_proba: List):
    return list(map(lambda array: model.classes_[array.argmax()], pred_proba))
