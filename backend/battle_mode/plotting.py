from typing import List, Tuple

import altair as alt
import pandas as pd


def learning_curve_plot(learning_data: pd.DataFrame) -> str:
    return alt.Chart(learning_data).mark_line().encode(
        alt.X('Iteration:O'),
        alt.Y('Value:Q'),
        color='Experiment:N'
    ).properties(width='container').to_json()


def confidence_histograms(conf_data: Tuple[List[List[float]], List[List[float]]]):
    return tuple([confidence_histogram_iteration(d) for d in conf_data])


def confidence_histogram_iteration(data: List[List[float]]):
    plots = []
    for it in data:
        chart = alt.Chart(data=pd.DataFrame({'Confidence': it})).mark_bar().encode(
            x=alt.X('Confidence', bin=alt.BinParams(maxbins=20), scale=alt.Scale(0.0, 1.0)),
            y=alt.Y('count()', type='ordinal')
        ).properties(width='container').to_json()
        plots.append(chart)
    return plots


# noinspection PyTypeChecker
def data_maps(data_map_data: Tuple[pd.DataFrame, pd.DataFrame]) -> Tuple[str, str]:
    return tuple([
        alt.Chart(data).mark_circle().encode(
            x=alt.X('Variability:Q'),
            y=alt.Y('Confidence:Q'),
            color='Correctness',
            tooltip=['Variability', 'Confidence', 'SampleID']
        ).properties(width='container').interactive().to_json()
        for data in data_map_data])


def vector_space(vector_space_data: Tuple[List[pd.DataFrame],List[pd.DataFrame]]) -> Tuple[List[str], List[str]]:
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
