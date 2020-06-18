import {State} from "@/store/models";

export const setDatasetType = (state: State, objectType: string) => {
    console.log("Setting new dataset type: " + objectType);
    state.datasetType = objectType;
};

export const setApiType = (state: State, objectType: string) => {
    console.log("Setting new API type: " + objectType);
    state.apiType = objectType;
};

export const startLoading = (state: State) => {
    state.loading = true;
};

export const endLoading = (state: State) => {
    state.loading = false;
};


export const setDatasets = function(state, newDatasets) {
	state.datasets = newDatasets;
}
