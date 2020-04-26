import {LabelPayload, State} from "@/store/models";

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

export const setImage = (state: State, data: any) => {
    state.image = data;
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
