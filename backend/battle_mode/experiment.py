import time

import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process
from multiprocessing.connection import Connection
import pandas as pd
from alipy.data_manipulate import split
from alipy.experiment import StoppingCriteria, StateIO, State
from alipy.index import IndexCollection
from sklearn.metrics import accuracy_score, f1_score

from ..models import AlExperimentConfig, QueryStrategyAbstraction


class ALExperimentProcess(Process):

    def __init__(self, d_frame: pd.DataFrame, config: AlExperimentConfig, pipe_endpoint: Connection):
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
        self.pipe_endpoint = pipe_endpoint
        self.metrics = pd.DataFrame(columns=['Acc', 'F1'])
        labeled_set = d_frame[d_frame['LABEL'].notnull()]
        all_labeled_samples = labeled_set.drop(labels='LABEL', axis='columns')
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

        # initiate configurable experiment setting
        self.unlab_ind = IndexCollection(
            [adjusted_idx_map[idx] for idx in unlabel_idx])  # Indexes of your unlabeled set for querying
        self.label_ind = IndexCollection([adjusted_idx_map[idx] for idx in label_idx])  # Indexes of your labeled set
        self.al_strategy = QueryStrategyAbstraction.build(qs_type=config.QUERY_STRATEGY,
                                                          X=self.all_training_samples.to_numpy(),
                                                          y=self.all_training_labels.to_numpy(),
                                                          config=config.QUERY_STRATEGY_CONFIG, )
        model_class = config.AL_MODEL.get_class()
        self.model = model_class()
        self.batch_size = config.BATCH_SIZE
        self.prediction_history = pd.DataFrame(columns=test_idx)
        self.stopping_criteria = StoppingCriteria(stopping_criteria=config.STOPPING_CRITERIA.get())

        self.X_test = all_labeled_samples.iloc[test_idx, :].to_numpy()
        self.y_test = labels.iloc[test_idx]
        self.state_saver = StateIO(round=0, train_idx=train_idx, test_idx=test_idx,
                                   init_U=self.unlab_ind.index, init_L=self.label_ind.index, verbose=False)

    def run(self, verbose=0):
        # initial training
        self.model.fit(*self.get_training_data())
        # test data does not change: has original index equal to all_labeled_samples

        iteration = 0
        while not self.stopping_criteria.is_stop():
            # query al_strategy for next samples
            selected_ind_list = self.al_strategy.select(label_index=self.label_ind, unlabel_index=self.unlab_ind,
                                                        model=self.model, batch_size=self.batch_size)
            self.label_ind.update(selected_ind_list)
            self.unlab_ind.difference_update(selected_ind_list)

            # train and test model
            start = time.time()
            try:
                self.model.fit(*self.get_training_data())
            except Exception as e:
                print(e)
                return
            finally:
                stop = time.time()
            diff_time = stop - start
            self.pipe_endpoint.send(diff_time)
            pred_proba = self.model.predict_proba(self.X_test)
            y_pred = list(map(lambda array: self.model.classes_[array.argmax()], pred_proba))
            perf = accuracy_score(y_true=self.y_test.to_list(), y_pred=y_pred)
            state = State(select_index=selected_ind_list, performance=perf)
            state.add_element(key='train_time', value=diff_time)
            self.state_saver.add_state(state)
            if verbose > 0:
                print(f"Training took: {diff_time}ms")
                print(f"Performance: {perf}")
                print(f"#Labeled: {len(self.label_ind.index)}")

            # add current iteration to history
            next_row = pd.Series(list(map(tuple, pred_proba)), index=self.prediction_history.columns)
            self.prediction_history = self.prediction_history.append(next_row, ignore_index=True)

            iteration += 1
            # update stopping_criteria
            self.stopping_criteria.update_information(self.state_saver)

        print(f"Stopped after {iteration} iterations")

    def get_training_data(self):
        return (
            self.all_training_samples.iloc[self.label_ind.index].to_numpy(),
            self.all_training_labels.iloc[self.label_ind.index].to_numpy())

    def calculate_metrics(self):
        # TODO
        # pandas dataframe: every column is one sample, every row is one prediction
        # every cell is a tuple of (predicted_label, certainty)
        assert len(self.state_saver) == len(self.prediction_history)

        num_iter = len(self.prediction_history)
        for idx, row in self.prediction_history.iterrows():
            y_pred = list(map(lambda probas: self.model.classes_[probas.index(max(probas))], row))
            acc = accuracy_score(self.y_test.to_list(), y_pred=y_pred)
            f1 = f1_score(self.y_test.to_list(), y_pred, average="micro")
            self.metrics = self.metrics.append({'ACC': acc, 'F1': f1}, ignore_index=True)
        acc_avg = self.metrics['ACC'].sum() / num_iter
        print(f"Accuracy over all iterations is: {acc_avg * 100}% ")
        print(
            f"Highest accuracy over all iterations is: {self.metrics['ACC'].max() * 100}% in iteration: {self.metrics['ACC'].idxmax()} ")
        f1_avg = self.metrics['F1'].sum() / num_iter
        print(f"F1 over all iterations is: {f1_avg * 100}% ")
        print(
            f"Highest f1 over all iterations is: {self.metrics['F1'].max() * 100}% in iteration: {self.metrics['F1'].idxmax()} ")
        training_times = [self.state_saver.get_state(i).get_value('train_time') for i in
                          range(len(self.prediction_history))]
        avg_time = round(sum(training_times) / num_iter, 4)
        print(f"Average training time took: " + ("less than 0.1ms" if avg_time < 0.1 else str(avg_time)))
        return self.metrics

    def _calc_confidence(self):
        return [np.max(row) for _, row in self.prediction_history.iterrows()]

    def plot_metrics(self):
        ax = plt.gca()
        ax.set_ylim([0, 1])
        plt.title("Accuracy over iterations")
        plt.plot(range(len(self.metrics)), self.metrics['ACC'])
        plt.show()
