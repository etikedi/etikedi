function delegateGetter(actionName, defaultValue) {
    return (state, getters) => {
		const apiType = getters.apiType
		if(apiType == "none"){
			console.log(
				"Root Store Ignoring Getter '" +
					actionName +
					"' for apiType none"
			);
			return defaultValue
		}
        console.log(
            "Root Store Delegating Getter '" +
                actionName +
                "' to current API type '" +
                apiType +
                "'"
        );
        return getters["api_" + apiType + "/" + actionName];
    };
}

export const sampleShortTitle = delegateGetter("sampleShortTitle", "");
export const prevButtonDisabled = delegateGetter("prevButtonDisabled", true);
export const nextButtonDisabled = delegateGetter("nextButtonDisabled", true);

export const apiType = function(state){
	const ds = state.activeDataset
	if(ds){
		if(ds.apiType){
			return ds.apiType;
		}
		return "default";
	}
	return "none";
}

export const datasetType = function(state) {
	const ds = state.activeDataset;
	if(!ds){
		return "none";
	}
	if(ds.datasetType){
		// the backend told us the DatasetType to display. Use this.
		return ds.datasetType;
	}
	// guess the dataset type (dumb approach)
	return "plaintext"
}
