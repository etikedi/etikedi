import {CifarSample, State} from "./models";

export const setCifarSample = (state: State, sample: CifarSample) => {
    state.cifarSample = sample;
};

export const setCifarLabels = (state: State, labels: any) => {
    state.cifarLabels = labels;
};
