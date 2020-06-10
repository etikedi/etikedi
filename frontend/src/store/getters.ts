function delegateGetter(actionName) {
    return (state, getters) => {
        console.log(
            "Root Store Delegating Getter '" +
                actionName +
                "' to current API type '" +
                state.apiType +
                "'"
        );
        return getters["api_" + state.apiType + "/" + actionName];
    };
}

export const activeDatasetId = delegateGetter("activeDatasetId");
export const labels = delegateGetter("labels");
