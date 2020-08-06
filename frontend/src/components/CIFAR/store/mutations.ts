import {LabelPayload, State} from "./models";

export const setCifarSample = (state: State, data: any) => {
    state.cifar = data;
};

export const nextCifarSample = (state: State) => {
    state.cifarId++;
};

export const prevCifarSample = (state: State) => {
    state.cifarId--;
};

export const changeLabel = (state: State, payload: LabelPayload) => {
    for (let i = payload.startId; i <= payload.endId; i++) {
        state.cifar.features[i][1]["label"] = payload.label;
    }
};