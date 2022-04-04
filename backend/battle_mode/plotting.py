from typing import List, Tuple

import altair as alt
import numpy as np
import pandas as pd

from ..models import DataMapsDTO, ClassificationBoundariesDTO
from ..utils import timeit


@timeit
def learning_curve_plot(learning_data: pd.DataFrame) -> str:
    return alt.Chart(learning_data).mark_line().encode(
        alt.X('Iteration:O'),
        alt.Y('Value:Q'),
        color='Experiment:N'
    ).properties(width='container').to_json()


@timeit
def confidence_histograms(conf_data: Tuple[List[List[float]], List[List[float]]]):
    return tuple([confidence_histogram_iteration(d) for d in conf_data])


def confidence_histogram_iteration(data: List[List[float]]):
    plots = []
    for it in data:
        chart = alt.Chart(data=pd.DataFrame({'Confidence': it})).mark_bar().encode(
            x=alt.X('Confidence', bin=alt.BinParams(maxbins=20), scale=alt.Scale(domain=[0.0, 1.0]),
                    axis=alt.Axis(values=np.arange(0, 1, .05))),
            y="count()"
        ).properties(width='container').to_json()
        plots.append(chart)
    return plots


@timeit
def data_maps(data_maps_data: DataMapsDTO) -> Tuple[List[str], List[str]]:
    return ([data_maps_iteration(it_data) for it_data in data_maps_data.exp_one_data],
            [data_maps_iteration(it_data) for it_data in data_maps_data.exp_two_data])


def data_maps_iteration(data_map_data_iteration: pd.DataFrame) -> str:
    """ 2D scatter plot
    points = Samples
    color: Percentage of correctness
    (mean of 10 iterations)
    X Axis: Variability
    Y Axis: Confidence
    """
    return alt.Chart(data_map_data_iteration).mark_circle().encode(
        x=alt.X('Variability:Q'),
        y=alt.Y('Confidence:Q'),
        color='Correctness',
        tooltip=['Variability', 'Confidence', 'SampleID']
    ).properties(width='container').interactive().to_json()


@timeit
def vector_space(vector_space_data: Tuple[List[pd.DataFrame], List[pd.DataFrame]]) -> Tuple[List[str], List[str]]:
    return [vector_space_iteration(it) for it in vector_space_data[0]], \
           [vector_space_iteration(it) for it in vector_space_data[1]]


def vector_space_iteration(iteration_data: pd.DataFrame) -> str:
    feature_1_name, feature_2_name = [x for x in iteration_data.columns if x not in ['Color', 'SampleID']]
    return alt.Chart(iteration_data).mark_circle().encode(
        x=f'{feature_1_name}:Q',
        y=f'{feature_2_name}:Q',
        color='Color',
        tooltip=list(iteration_data.columns)
    ).properties(width='container').interactive().to_json()


@timeit
def classification_boundaries(cb_data: ClassificationBoundariesDTO):
    def classification_boundaries_iteration(iteration_data: pd.DataFrame):
        feature_1_name, feature_2_name = cb_data.reduced_features.columns
        merged = pd.merge(cb_data.reduced_features, iteration_data, left_index=True, right_index=True)
        return alt.Chart(merged).mark_point().encode(
            x=f'{feature_1_name}:Q',
            y=f'{feature_2_name}:Q',
            color=alt.Color('Class:O', scale=alt.Scale(scheme='tableau10')),
            shape='Class:O',
            opacity='Confidence:Q'
        ).properties(width='container').to_json()

    return [classification_boundaries_iteration(it) for it in cb_data.exp_one_iterations], \
           [classification_boundaries_iteration(it) for it in cb_data.exp_two_iterations]
