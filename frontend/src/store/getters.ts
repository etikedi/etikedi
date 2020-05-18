function delegateGetter(actionName) {
    return (state, getters) => {
        console.log(
            "Root Store Delegating Getter '" +
                actionName +
                "' to current datasetType '" +
                state.datasetType +
                "'"
        );
        return getters[state.datasetType + "/" + actionName];
    };
}

export const activeDatasetId = delegateGetter("activeDatasetId");
export const labels = delegateGetter("labels");
