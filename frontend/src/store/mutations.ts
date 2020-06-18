import {State} from "@/store/models";

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


export const setDatasets = function(state, {datasets}) {
	// translate array-based format into key-value store used by view
	const newDatasets = {};
	for (const dataset of datasets) {
		newDatasets[dataset.id] = dataset;
	}
	console.log("Received available datasets from server:");
	console.log(newDatasets);
	state.datasets = newDatasets;
}

export const setActiveDatasetId = function(state, datasetId) {
	state.activeDatasetId = datasetId;
}

export const setActiveDataset = function(state, dataset) {
	state.activeDataset = dataset;
}

export const setLabels = function(state, labels) {
	state.labels = labels;
}
