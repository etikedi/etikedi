import api from "@/api/DummyAergiaDefaultApiService"

function delegateAction(actionName) {
    return ({dispatch, commit, state, getters}) => {
		const apiType = getters.apiType
		if(apiType == "none"){
			console.log(
				"Root Store Ignoring Action '" +
					actionName +
					"' for apiType none"
			);
			return;
		}
        console.log(
            "Root Store Delegating Action '" +
                actionName +
                "' to current API type '" +
                apiType +
                "'"
        );
        dispatch("api_" + apiType + "/" + actionName);
    };
}

export const nextSample = delegateAction("nextSample");

export const prevSample = delegateAction("prevSample");

export const loadSample = delegateAction("loadSample");

export const labelSample = delegateAction("labelSample");


export const setActiveDatasetId = function({dispatch, commit, state}, datasetId) {
	commit("setActiveDatasetId", datasetId);
	dispatch("updateActiveDataset");
}

export const loadAllDatasets = function({dispatch, commit, state}) {
	commit("startLoading")
	api.getAllDatasets().then(function(data) {
		commit("setDatasets", {datasets: data.datasets});
		dispatch("updateActiveDataset");
	})
}

export const updateActiveDataset = function({dispatch, commit, state}) {
	console.log("Updating active dataset")
	if(state.activeDatasetId){
		const ds = state.datasets[state.activeDatasetId];
		if(ds){
			// To set the active dataset, both an activeDatasetId must have been set (this is done by LabelView via the Route)
			// and the list of datasets must have been retrieved (the Header view is responsible for this)
			console.log("Active dataset found:")
			console.log(ds)
			commit("setActiveDataset", ds);
			// we can now retrieve the first sample
			dispatch("loadSample");
			dispatch("loadLabels");
			return;
		}
	}
	console.log("None loaded")
	commit("setActiveDataset", null);
	commit("endLoading")
}

export const loadLabels = function({dispatch, commit, state}) {
	if(!state.activeDatasetId){
		commit("setLabels", []);
	}
	api.getLabels({datasetId: state.activeDatasetId}).then(function(data) {
		commit("setLabels", data.labels);
	})
}
