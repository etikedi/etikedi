import {CifarSample, State} from "./models";

/*
export const setImage = (state: State, data: any) => {
    state.image = data;
};
 */

export const setAllDatasets = (state: State, allDatasets: string[]) => {
    state.allDatasets = allDatasets;
};

export const setCurrentDataset = (state: State, currentDataset: string) => {
    state.currentDataset = currentDataset;
};

export const setCifarSampleID = (state: State, sampleID: any) => {
    state.cifarSampleID = sampleID;
};

export const setCifarSample = (state: State, sample: CifarSample) => {
    state.cifarSample = sample;
};

export const setCifarLabels = (state: State, labels: any) => {
    state.cifarLabels = labels;
};

export const startLoading = (state: State) => {
    state.loading = true;
};

export const endLoading = (state: State) => {
    state.loading = false;
};

export const toggleShowFeatureTooltips = (state: State, newValue: boolean) => {
    state.displayFeatureTooltips = newValue;
};
