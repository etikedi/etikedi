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

export const nextDataset = delegateAction("nextDataset");

export const prevDataset = delegateAction("prevDataset");

export const loadDataset = delegateAction("loadDataset");

export const labelDataset = delegateAction("labelDataset");
