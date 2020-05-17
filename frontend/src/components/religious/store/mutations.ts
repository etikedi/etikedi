import {LabelPayload, State} from "@/store/models";

export const setRT = (state: State, data: any) => {
    state.religiousText = data;
};

export const nextRT = (state: State) => {
    if (state.rtId == 1) {
        state.prevButtonDisabled = false;
    }
    state.rtId++;
};

export const prevRT = (state: State) => {
    if (state.rtId == 2) {
        state.prevButtonDisabled = true;
    }
    state.rtId--;
};

export const changeLabel = (state: State, payload: LabelPayload) => {
    state.religiousText.features["label"] = payload.label;
};
