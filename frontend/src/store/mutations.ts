import {State} from "@/store/models";

export const setDatasetType = (state: State, objectType: string) => {
    console.log("Setting new dataset type: " + objectType);
    state.datasetType = objectType;
};

export const startLoading = (state: State) => {
    //state.loading = true;
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

export const toggleShowFeatureTooltipsSwitch = (state: State, newValue: boolean) => {
    state.displayFeatureTooltipsSwitch = newValue;
};

export const toggleIsHomePage = (state: State, newValue: boolean) => {
    state.isHomePage = newValue;
};
