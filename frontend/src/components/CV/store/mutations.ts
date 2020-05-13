import {LabelPayload, State} from "./models";

export const setCv = (state: State, data: any) => {
    state.cv = data;
};

export const nextCv = (state: State) => {
    state.cvId++;
};

export const prevCv = (state: State) => {
    state.cvId--;
};

export const changeLabel = (state: State, payload: LabelPayload) => {
    for (let i = payload.startId; i <= payload.endId; i++) {
        state.cv.features[i][1]["label"] = payload.label;
    }
};
