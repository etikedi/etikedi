import {CifarSample, State} from "./models";

/*
export const setImage = (state: State, data: any) => {
    state.image = data;
};
 */

export const setCifarSampleID = (state: State, sampleID: any) => {
    state.cifarSampleID = sampleID;
};

export const setCifarSample = (state: State, sample: CifarSample) => {
    state.cifarSample = sample;
};

export const setCifarLabels = (state: State, labels: any) => {
    state.cifarLabels = labels;
};
