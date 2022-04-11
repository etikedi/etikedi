from typing import List, Tuple, Union

import altair as alt
import numpy as np
import pandas as pd
from altair import UrlData

from ..models import ClassificationBoundariesDTO, DataMapsDTO, VectorSpaceDTO
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
    return ([data_maps_iteration(it_data) for it_data in data_maps_data.exp_one_iterations],
            [data_maps_iteration(it_data) for it_data in data_maps_data.exp_two_iterations])


def data_maps_iteration(data_map_data_iteration: Union[UrlData, pd.DataFrame]) -> str:
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
        color='Correctness:Q',
        tooltip=['Variability:Q', 'Confidence:Q', 'SampleID:O']
    ).properties(width='container').interactive().to_json()


@timeit
def vector_space(vector_space_data: VectorSpaceDTO) -> Tuple[List[str], List[str]]:
    f1, f2 = vector_space_data.feature_one_name, vector_space_data.feature_two_name
    return [vector_space_iteration(it, f1, f2) for it in vector_space_data.exp_one_iterations], \
           [vector_space_iteration(it, f1, f2) for it in vector_space_data.exp_two_iterations]


def vector_space_iteration(
        iteration_data_url: Union[UrlData, pd.DataFrame],
        feature_1_name: str,
        feature_2_name: str) -> str:
    f1_enc = f'{feature_1_name}:Q'
    f2_enc = f'{feature_2_name}:Q'
    return alt.Chart(iteration_data_url).mark_circle().encode(
        x=f1_enc,
        y=f2_enc,
        color='Color:N',
        tooltip=[f1_enc, f2_enc, 'Color:N', 'SampleID:O']
    ).properties(width='container').interactive().to_json()


@timeit
def classification_boundaries(cb_data: ClassificationBoundariesDTO):
    def classification_boundaries_iteration(iteration_data: Union[UrlData, pd.DataFrame],
                                            feature_1_name: str,
                                            feature_2_name: str):
        return alt.Chart(iteration_data).mark_rect().encode(
            x=alt.X(f'{feature_1_name}:Q', bin=alt.Bin(maxbins=cb_data.x_bins)),
            y=alt.Y(f'{feature_2_name}:Q', bin=alt.Bin(maxbins=cb_data.y_bins)),
            color=alt.Color('Class:O', scale=alt.Scale(scheme='tableau10')),
            opacity='Confidence:Q'
        ).properties(width='container').to_json()

    f1, f2 = cb_data.feature_one_name, cb_data.feature_two_name
    return [classification_boundaries_iteration(it, f1, f2) for it in cb_data.exp_one_iterations], \
           [classification_boundaries_iteration(it, f1, f2) for it in cb_data.exp_two_iterations]
