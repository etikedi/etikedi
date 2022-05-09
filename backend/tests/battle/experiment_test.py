import math
import time
from typing import List, Tuple

import numpy as np
import pandas as pd

import pytest
from scipy.sparse.linalg import ArpackError

from ...battle_mode.experiment import ALExperimentProcess
from ..mocks.MockQueue import MockQueue
from ...models import (
    QueryStrategyType,
    ALBattleConfig,
    ExperimentResults,
    AlExperimentConfig,
    ExperimentQueueEvent,
    ExperimentQueueEventType,
    StoppingCriteriaOption,
    QKernel,
    QMeasureType,
    QMetric,
    ALModel
)

test_data: pd.DataFrame = pd.read_csv("backend/tests/battle/test_data.csv")
test_data_cb_sample: pd.DataFrame = pd.read_csv("backend/tests/battle/test_data_cb_raster.csv", index_col=0)


# TODO parametrize configs

@pytest.fixture(params=list(QKernel))
def qkernel(request):
    return request.param


@pytest.fixture(params=list(QMeasureType))
def qmeasure_type(request):
    return request.param


@pytest.fixture(params=list(QMetric))
def qmetric(request):
    return request.param


@pytest.fixture(params=list(ALModel))
def al_model(request):
    return request.param


@pytest.fixture(params=list(StoppingCriteriaOption))
def stopping_criteria(request) -> Tuple:
    criteria: StoppingCriteriaOption = request.param
    criteria_value = None
    if criteria == StoppingCriteriaOption.NUM_OF_QUERIES:
        criteria_value = 10
    elif criteria == StoppingCriteriaOption.PERCENT_OF_UNLABEL:
        criteria_value = 0.3
    elif criteria == StoppingCriteriaOption.COST_LIMIT:
        criteria_value = 10
    elif criteria == StoppingCriteriaOption.CPU_TIME:
        criteria_value = 300  # cpu time perf_counter() - start_time

    return criteria, criteria_value


@pytest.fixture(params=[
    QueryStrategyType.QUERY_INSTANCE_BMDR,
    QueryStrategyType.QUERY_INSTANCE_GRAPH_DENSITY,
    QueryStrategyType.QUERY_INSTANCE_QBC,
    QueryStrategyType.QUERY_INSTANCE_QUIRE,
    QueryStrategyType.QUERY_INSTANCE_SPAL,
    QueryStrategyType.QUERY_INSTANCE_UNCERTAINTY,
    QueryStrategyType.QUERY_INSTANCE_RANDOM,
    QueryStrategyType.QUREY_EXPECTED_ERROR_REDUCTION
])
def experiment_config(request, al_model) -> AlExperimentConfig:
    strategy: QueryStrategyType = request.param
    experiment_config = AlExperimentConfig(
        QUERY_STRATEGY=strategy,
        AL_MODEL=al_model
    )
    experiment_config.QUERY_STRATEGY_CONFIG=strategy.get_default_config()
    return experiment_config


@pytest.fixture()
def complete_battle(experiment_config, stopping_criteria):
    exp_id = 0
    samples_df = test_data.copy()
    cb_sample = test_data_cb_sample.copy()
    exp_conf_one = experiment_config
    exp_config_two = AlExperimentConfig()  # not important
    criteria, stopping_value = stopping_criteria
    config = ALBattleConfig(
        exp_configs=(exp_conf_one, exp_config_two),
        STOPPING_CRITERIA=criteria,
        STOPPING_CRITERIA_VALUE=stopping_value
    )
    queue = MockQueue()
    # noinspection PyTypeChecker Queue
    yield ALExperimentProcess(exp_id=exp_id,
                              samples_df=samples_df,
                              battle_config=config,
                              queue=queue,
                              cb_sample=cb_sample)


def test_start(complete_battle):
    # NOTE this method has currently 240 test instances and will take some time.
    # tests matrix of configuration of strategy x stopping-criteria x al_model
    battle_config = complete_battle.battle_config
    samples_df = complete_battle.samples_df
    q = complete_battle.queue
    start_ns = time.perf_counter_ns()
    try:
        complete_battle.run()
    except ArpackError as e:
        pytest.skip("Acceptable failure with error: " + repr(e))
    end_ns = time.perf_counter_ns()
    total_time_measured = (end_ns - start_ns) * 1e-9  # total time in seconds
    assert not q.empty()
    events: List[ExperimentQueueEvent] = [q.get() for _ in range(q.qsize())]
    # analyze results
    results: ExperimentResults = _assert_finished_successfully(events, battle_config)
    all_sample_ids = test_data["DB_ID"].array
    all_labels = test_data["LABEL"].unique()
    _assert_correct_ids(all_sample_ids, test_data_cb_sample, results)
    # otherwise, experiment is allowed to adjust the split
    if battle_config.TRAIN_TEST_SPLIT * len(samples_df) > len(all_labels):
        # assert correctly traint split ratio
        test_sample_size = abs(battle_config.TRAIN_TEST_SPLIT * len(samples_df))
        assert (test_sample_size - len(results.raw_predictions.columns) < 5)
    _assert_meta_data(all_sample_ids, total_time_measured, battle_config, results)
    # model classes should be all label in the dataset
    assert set(all_labels) == set(results.classes)


def _assert_finished_successfully(events: List[ExperimentQueueEvent], config: ALBattleConfig) -> ExperimentResults:
    assert any(e.event_type == ExperimentQueueEventType.SETUP_COMPLETED for e in events)
    assert any(e.event_type == ExperimentQueueEventType.INFO for e in events)
    error = next((e for e in events if e.event_type == ExperimentQueueEventType.FAILED), None)
    if error is not None:
        pytest.fail(f"Test failed for config: {config} with error: {error.value}.\nThis may be acceptable.")
    results_event = next((e for e in events if e.event_type == ExperimentQueueEventType.RESULT), None)
    assert results_event is not None
    return results_event.value


def _assert_correct_ids(all_sample_ids, test_cb_sample, results: ExperimentResults):
    # all ids of test samples should be in the original dataset
    assert all(smpl in all_sample_ids for smpl in results.raw_predictions.columns)  # subset
    # the provided cb_sample are used
    assert set(results.cb_predictions.columns.array) == set(test_cb_sample.index)
    # correct_label_as_idx
    for db_id, index_of_class in results.correct_label_as_idx.items():
        assert db_id in all_sample_ids
        assert 0 <= index_of_class < len(results.classes)


def _assert_meta_data(all_sample_ids, total_time_measured, battle_config, results: ExperimentResults):
    for iteration, meta_per_iter in enumerate(results.meta_data):
        assert all(smpl in all_sample_ids for smpl in meta_per_iter.sample_ids)
        if iteration != len(results.meta_data) - 1:  # number of sample may not be dividable by batch size
            assert len(meta_per_iter.sample_ids) == battle_config.BATCH_SIZE
    training_time_reported = sum(m.time for m in results.meta_data)
    assert total_time_measured >= training_time_reported  # total time reported does not include setup time
    if battle_config.STOPPING_CRITERIA == StoppingCriteriaOption.ALL_LABELED:
        assert math.isclose(results.meta_data[-1].percentage_labeled, 1.0, abs_tol=0.001)
        # all samples that are not in the test == all samples that were initially labeled and labeled in the process
        assert (set(all_sample_ids).difference(set(results.raw_predictions.columns))
                == set(list(np.concatenate([m.sample_ids for m in results.meta_data])) + results.initially_labeled))
