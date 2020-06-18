import api from "@/api/AergiaDefaultApiService"

function delegateAction(actionName) {
    return ({dispatch, commit, state}) => {
        console.log(
            "Root Store Delegating Action '" +
                actionName +
                "' to current API type '" +
                state.apiType +
                "'"
        );
        dispatch("api_" + state.apiType + "/" + actionName);
    };
}

export const nextSample = delegateAction("nextSample");

export const prevSample = delegateAction("prevSample");

export const loadSample = delegateAction("loadSample");

export const labelSample = delegateAction("labelSample");


export const loadAllDatasets = function({dispatch, commit, state}) {
	api.getAllDatasets().then(function(datasetsIn) {
		const newDatasets = {};
		for (const dataset in datasetsIn) {
			newDatasets[dataset.id] = dataset;
		}
		commit("setDatasets", newDatasets);
	})
}
