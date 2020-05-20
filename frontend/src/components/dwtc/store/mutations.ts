import {LabelPayload, State} from "./models";

export const setDWTC = (state: State, data: any) => {
    state.dwtc = data;
};

export const nextDWTC = (state: State) => {
    state.dwtcId++;
};

export const prevDWTC = (state: State) => {
    state.dwtcId--;
};

export const changeLabel = (state: State, payload: LabelPayload) => {
    for (let i = payload.startId; i <= payload.endId; i++) {
        state.dwtc.features[i][1]["label"] = payload.label;
    }
};
