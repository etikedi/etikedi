import DWTCService from '@/api/DWTC-Service';

export const nextDataset = (
    {dispatch, commit}: any
) => {
    commit('nextDWTC');
    dispatch('loadDataset');
};

export const prevDataset = (
    {dispatch, commit}: any
) => {
    commit('prevDWTC');
    dispatch('loadDataset');
};

export const loadDataset = (
    {commit, state}: any
) => {
	console.log("Loading current DWTC " + state.dwtcId)
    commit("startLoading", null, { root: true });// calls in root store, loading handled globally
    return DWTCService.getDWTC({dwtcId: state.dwtcId}).then((data) => {
        commit('setDWTC', data);
        commit("endLoading", null, { root: true });// calls in root store, loading handled globally
    })
};

export const labelDataset = (
    {commit}: any,
    label: string
) => {
    const selection = window.getSelection();

    // window.console.log(label);
    // window.console.log(selection);
    function findFeatureId(target: Node | null | undefined): HTMLElement | null | undefined {
        let derivedTarget: HTMLElement | null | undefined;

        if (target?.nodeType != 1) {
            derivedTarget = target?.parentElement;
        } else {
            derivedTarget = target as HTMLElement
        }

        while (derivedTarget && !derivedTarget.hasAttribute("feature_id")) {
            derivedTarget = derivedTarget?.parentElement;
            window.console.log(derivedTarget);
        }

        return derivedTarget;
    }

    let startId = Number(findFeatureId(selection?.anchorNode)?.getAttribute("feature_id"));
    let endId = Number(findFeatureId(selection?.focusNode)?.getAttribute("feature_id"));


    // window.console.log(startId);
    // window.console.log("end" + endId);
    if (startId > endId) {
        const temp = startId;
        startId = endId;
        endId = temp;
    }
    // window.console.log("start" + startId);
    // window.console.log("end" + endId);

    commit('changeLabel', {startId, endId, label});
    window.getSelection()?.removeAllRanges();
};
