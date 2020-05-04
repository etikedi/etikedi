import {CifarSample, LabelPayload, State} from "@/store/models";

export const setCv = (state: State, data: any) => {
    state.cv = data;
};

export const nextCv = (state: State) => {
    if (state.cvId == 1) state.prevButtonDisabled = false;
    state.cvId++;
};

export const prevCv = (state: State) => {
    if (state.cvId == 2) {
        state.prevButtonDisabled = true;
        state.cvId--;
    } else {
        state.cvId--;
    }
};

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

export const changeLabel = (state: State, payload: LabelPayload) => {
    for (let i = payload.startId; i <= payload.endId; i++) {
        state.cv.features[i][1]["label"] = payload.label;
    }
};

export const toggleShowFeatureTooltips = (state: State, newValue: boolean) => {
    state.displayFeatureTooltips = newValue;
};
