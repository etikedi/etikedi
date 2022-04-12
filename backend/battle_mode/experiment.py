from __future__ import annotations  # necessary in order to use ALExperimentProcess as type hint

import random
import time
from math import ceil
from multiprocessing import Process
from multiprocessing import Queue
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from alipy.data_manipulate import split
from alipy.experiment import StoppingCriteria, StateIO, State
from alipy.index import IndexCollection
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, auc, pairwise_distances

from ..models import (
    ALModel,
    ALBattleConfig,
    AlExperimentConfig,
    QueryStrategyAbstraction,
    MetaData,
    ExperimentResults,
    StoppingCriteriaOption,
    MetricsDFKeys,
    StateIOValueKeys,
    ExperimentQueueEventType,
    ExperimentQueueEvent)
from ..utils import timeit

# type-alias
Lateinit = Optional  # the attributes are not optional but initialisation is postponed to async execution


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

            # the increment between consecutive iterations averaged
            incr = sum(self._times[i + 1] - self._times[i] for i in range(it - 1)) / max(it - 1, 1)
            # assuming linear time increase to train the model
            result = sum([last_training_time + incr * i for i in range(self._total_iterations - it)])
            if result < 0.0:
                print(f"[Warning] Remaining time is negative: {result}")
            return result * 1e-9  # convert ns to seconds

        def start_timer(self):
            if self._criteria != StoppingCriteriaOption.CPU_TIME:
                raise ValueError(f"This method is only relevant if criteria is : {StoppingCriteriaOption.CPU_TIME}")
            # not one to one what alipy is using but necessary for estimation
            self._start_time = time.perf_counter_ns()

    def __init__(self,
                 exp_id: int,
                 samples_df: pd.DataFrame,
                 battle_config: ALBattleConfig,
                 queue: Queue,
                 cb_sample: pd.DataFrame):
        """
        @param exp_id in [0,1] identifies this experiment
        @param samples_df all samples in the dataset that have at least one label
            required columns are DB_ID and LABEL each other column should be one feature
        @param queue the multiprocessing queue to transfer update information and the final results
        @param cb_sample randomly generated sample for classification boundaries
            each column should be a feature, each row should be a sample
        """
        super().__init__()
        # Randomly generated sample for classification boundaries
        self.cb_sample_as_numpy: np.ndarray = cb_sample.to_numpy()
        # prediction per iteration for each cb_sample
        # column = sample, row = iteration, cell = tuple of confidence scores (one for each class)
        self.cb_sample_predictions: pd.DataFrame = pd.DataFrame()
        # zero or one to identify print outputs
        self.exp_id = exp_id
        self.battle_config: ALBattleConfig = battle_config
        self.exp_config: AlExperimentConfig = battle_config.exp_configs[exp_id]
        self.queue: Queue = queue
        model_class = self.exp_config.AL_MODEL.get_class()
        self.model = model_class() if self.exp_config.AL_MODEL != ALModel.SVC else model_class(probability=True)
        self.stopping_criteria = StoppingCriteria(stopping_criteria=battle_config.STOPPING_CRITERIA.get()) \
            if (battle_config.STOPPING_CRITERIA_VALUE is None) \
            else StoppingCriteria(battle_config.STOPPING_CRITERIA.get(), battle_config.STOPPING_CRITERIA_VALUE)
        self.batch_size: int = battle_config.BATCH_SIZE  # number of samples to be labeled each iteration
        # move time intensive data operations outside __init__
        # all sample in this dataset. Used for train-test split
        # column = feature, row = sample, required columns = DB_ID and LABEL
        self.samples_df: pd.DataFrame = samples_df
        # the trainings' subset of self.samples_df (without DB_ID and LABEL]
        self.all_training_samples = None
        # the trainings' subset of self.samples_df but only the label
        self.all_training_labels = None
        # the al-strategy requires the index lists to be from 0 to some n therefore DB_ID can't be used as natural index
        # these maps save witch DB_ID was replaced by which index
        self.idx2IDTrain: Lateinit[Dict[int, int]] = None
        self.idx2IDTest: Lateinit[Dict[int, int]] = None
        # the alipy Index collection which keep track over which sample are labeled
        self.unlab_ind: Lateinit[IndexCollection] = None
        self.label_ind: Lateinit[IndexCollection] = None
        # for each test sample keep track what the model predicted for each iteration
        # column = sample_id (DB_ID), row = iteration, cell = tuple of confidence scores (one for each class)
        self.prediction_history: Lateinit[pd.DataFrame] = None
        self.X_test: Lateinit[np.ndarray] = None  # all test samples as numpy array (feature matrix)
        self.y_test: Lateinit[np.ndarray] = None  # all test labels (label vector)
        self.state_saver: Lateinit[StateIO] = None  # alipy state io to keep track of additional meta information
        # RemainingTimeEstimate instance predicting the remaining time
        self.rte: Lateinit[ALExperimentProcess.RemainingTimeEstimate] = None

    @timeit
    def _setup(self):
        print(f"[{self.exp_id}] Loaded dataset")
        labeled_set = self.samples_df[self.samples_df['LABEL'].notnull()]
        all_labeled_samples = labeled_set.drop(labels=['LABEL', 'DB_ID'], axis='columns')
        labels = labeled_set['LABEL']

        # Adjust train-test split and initially labeled such that for each class (label)
        # there can be at least one sample in the initially labeled training set.
        label_num = len(np.unique(labels))
        number_of_instances = len(all_labeled_samples)
        initially_labeled = self.battle_config.INITIALLY_LABELED
        train_test_split = self.battle_config.TRAIN_TEST_SPLIT
        if round((1 - train_test_split) * number_of_instances) < label_num:
            train_test_split = (1 - label_num / number_of_instances)
        # set initially_labeled such that at least one sample per class will be in the initially labeled training-set
        if round((1 - train_test_split) * initially_labeled * number_of_instances) < label_num:
            initially_labeled = (1 + label_num) / ((1 - train_test_split) * number_of_instances)

        # fix randomness
        np.random.seed(self.battle_config.RANDOM_SEED)
        random.seed(self.battle_config.RANDOM_SEED)
        # data split:
        # all_labeled_samples are all samples for the dataset that have at least one label
        # the index is equal to the id in the dataset
        #   train_idx union test_idx = all_labeled_samples
        #       label_idx union unlabel_idx = train_idx
        train_idx, test_idx, label_idx, unlabel_idx = split(
            X=all_labeled_samples,
            y=labels.to_numpy(),
            test_ratio=train_test_split,
            split_count=1,
            all_class=True,
            initial_label_rate=initially_labeled,
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

        self.idx2IDTrain = {new_idx: self.samples_df.iloc[idx]['DB_ID'] for new_idx, idx in enumerate(train_idx)}
        self.idx2IDTest = {idx: self.samples_df.iloc[idx]['DB_ID'] for idx in test_idx}

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
        # raw data for predictions
        self.X_test = all_labeled_samples.iloc[test_idx, :].to_numpy()
        self.y_test = labels.iloc[test_idx]
        self.state_saver: StateIO = StateIO(round=0, train_idx=train_idx, test_idx=test_idx,
                                            init_U=self.unlab_ind.index, init_L=self.label_ind.index,
                                            verbose=False)
        self.rte = ALExperimentProcess.RemainingTimeEstimate(self.battle_config.STOPPING_CRITERIA, self)

    def run(self, verbose=0):
        """
        @param verbose: debug-level
        Main entry-point for async execution.
        Normal procedure: IN_SETUP -> TRAINING -> COMPLETED
        """
        # catch possible exceptions and send them over the queue
        try:
            self._setup()
            setup_completed = ExperimentQueueEvent(event_type=ExperimentQueueEventType.SETUP_COMPLETED, value=True)
            self.queue.put(setup_completed, False)
            self._train(verbose)
            training_completed = ExperimentQueueEvent(event_type=ExperimentQueueEventType.RESULT,
                                                      value=self._get_result())
            self.queue.put(training_completed, False)
            print(f"[{self.exp_id}] Process finished ")
        except Exception as e:
            error_event = ExperimentQueueEvent(event_type=ExperimentQueueEventType.FAILED, value=repr(e))
            self.queue.put(error_event, False)
            print(f"[{self.exp_id}] Process failed: {repr(e)}")
            raise e

    def _train(self, verbose):
        """
        The main method executed in state TRAINING.
        @param verbose: debug-level
        The training-loop consists of:
            1.query al-strategy which sample should be labeled next.
            2. update label / unlabel index
            3. train al-model with new information
            4. report training time over queue
            5. get prediction for each test sample
            6. store meta information in state-io
            7. store predictions in list
            8. update stopping criteria
            9. repeat until stopping criteria is met

        """
        self.model.fit(*self._get_training_data())
        # test data does not change: has original index equal to all_labeled_samples

        iteration: int = 1
        # faster if predictions are stores as list then appending to df each iteration
        # list-entry = iteration, dict: db_id -> tuple of confidence scores
        predictions: List[Dict[int, Tuple[float]]] = []
        cb_sample_predictions = []  # same as predictions just for the classification-boundaries sample
        if self.battle_config.STOPPING_CRITERIA == StoppingCriteriaOption.CPU_TIME:
            self.stopping_criteria.reset()  # reset cpu start time 
            self.rte.start_timer()
        starting_time = time.time_ns()  # time to measure complete training over all iterations
        while not self.stopping_criteria.is_stop():
            # 1. query al_strategy for next samples
            selected_ind_list = self.al_strategy.select(label_index=self.label_ind,
                                                        unlabel_index=self.unlab_ind,
                                                        model=self.model,
                                                        batch_size=self.batch_size)
            # 2.
            self.label_ind.update(selected_ind_list)
            self.unlab_ind.difference_update(selected_ind_list)

            # 3. train and test model
            start = time.time_ns()
            self.model.fit(*self._get_training_data())
            stop = time.time_ns()
            diff_time = stop - start
            estimation = self.rte.remaining_time(diff_time)
            if iteration > 2 and estimation >= 0:  # estimation not precise enough
                self.queue.put(  # 4.
                    ExperimentQueueEvent(event_type=ExperimentQueueEventType.INFO, value=estimation),
                    False)
                if verbose > 0:
                    print(f"[{self.exp_id}] estimation: {estimation}")
            # 5. return tuple of confidence scores for each class for each sample in X_test
            pred_proba = self.model.predict_proba(self.X_test)
            y_pred = _predicted_class(self.model, pred_proba)  # get label according to the highest confidence score
            # 6. store meta information in state io
            perf = accuracy_score(y_true=self.y_test.to_list(), y_pred=y_pred)
            state = State(select_index=selected_ind_list, performance=perf)
            state.add_element(key=StateIOValueKeys.TIME, value=round(diff_time * 1e-9, 4))  # store time in seconds
            state.add_element(key=StateIOValueKeys.PERC_LABELED,
                              value=len(self.label_ind) / (len(self.unlab_ind) + len(self.label_ind)))
            self.state_saver.add_state(state)
            if verbose > 0:
                print(f"[{self.exp_id}] Training took: {diff_time}ns")
                print(f"[{self.exp_id}] Performance: {perf}")
                print(f"[{self.exp_id}] #Labeled: {len(self.label_ind.index)}")

            # 7. add current iteration to history
            # save samples by db_id
            predictions.append(
                {self.idx2IDTest[x]: pred for (x, pred) in zip(self.state_saver.test_idx, map(tuple, pred_proba))}
            )
            # classify the random sample used for classification boundaries
            cb_sample_predictions.append(list(map(tuple, self.model.predict_proba(self.cb_sample_as_numpy))))

            iteration += 1
            # 8. update stopping_criteria
            self.stopping_criteria.update_information(self.state_saver)

        print(f"[{self.exp_id}] Stopped after {iteration} iterations")
        print(f"[{self.exp_id}] Training took {round((time.time_ns() - starting_time) * 1e-9, 4)} seconds")
        self.prediction_history = pd.DataFrame(predictions)
        self.cb_sample_predictions = pd.DataFrame(cb_sample_predictions)

    def _get_training_data(self):
        return (
            self.all_training_samples.iloc[self.label_ind.index].to_numpy(),
            self.all_training_labels.iloc[self.label_ind.index].to_numpy())

    def _get_result(self) -> ExperimentResults:
        assert len(self.state_saver) == len(self.prediction_history)
        # for each test sample save the correct label
        # as each prediction for each test sample is a tuple of confidence scores save the correct label as index
        # such that conf_tuple.index(max(conf_tuple)) = correct_label_as_idx
        correct_label_as_idx = {self.idx2IDTest[idx]: self.model.classes_.tolist().index(label_str)
                                for idx, label_str in self.y_test.items()}
        assert all([smpl_id in correct_label_as_idx for smpl_id in self.prediction_history.columns])
        metric_scores = self._calc_metrics_scores()
        meta_data = self._convert_states_data()

        result = ExperimentResults(
            raw_predictions=self.prediction_history,
            cb_predictions=self.cb_sample_predictions,
            metric_scores=metric_scores,
            initially_labeled=[self.idx2IDTrain[idx] for idx in self.state_saver.init_L],
            correct_label_as_idx=correct_label_as_idx,
            meta_data=meta_data,
            classes=self.model.classes_,
        )
        return result

    def _calc_metrics_scores(self) -> pd.DataFrame:
        """
        Calculate Acc, F1, Recall, Precision
        @return: pandas dataframe where columns = MetricsDFKeys and each row is one iteration
        """
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
        for idx in metric_scores.index[1:]:
            # idx +1 because current iteration should be included in calculation
            auc_ = auc(list(range(idx + 1)), metric_scores[MetricsDFKeys.F1].iloc[:idx + 1])
            # auc(...) / idx in order to normalize the area under the curve
            normalised_auc = auc_ / idx
            metric_scores.loc[idx, MetricsDFKeys.F1_AUC] = normalised_auc

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
            selected_idx = state.get_value(StateIOValueKeys.SAMPLES)  # list of indices
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

    def _convert_states_data(self) -> List[MetaData]:
        state_data = []
        for idx, state in enumerate(self.state_saver):
            # transform index of samples back to id in database
            selected_samples = [self.idx2IDTrain[i] for i in state.get_value(StateIOValueKeys.SAMPLES)]
            metric_dp: MetaData = MetaData(time=state.get_value(StateIOValueKeys.TIME),
                                           percentage_labeled=state.get_value(StateIOValueKeys.PERC_LABELED),
                                           sample_ids=selected_samples)
            state_data.append(metric_dp)
        return state_data


def _predicted_class(model, pred_proba: List):
    return list(map(lambda array: model.classes_[array.argmax()], pred_proba))
