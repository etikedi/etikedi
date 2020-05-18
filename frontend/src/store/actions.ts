function delegateAction(actionName) {
    return ({dispatch, commit, state}) => {
        console.log(
            "Root Store Delegating Action '" +
                actionName +
                "' to current datasetType '" +
                state.datasetType +
                "'"
        );
        dispatch(state.datasetType + "/" + actionName);
    };
}

export const nextDataset = delegateAction("nextDataset");

export const prevDataset = delegateAction("prevDataset");

export const loadDataset = delegateAction("loadDataset");

export const labelDataset = delegateAction("labelDataset");
