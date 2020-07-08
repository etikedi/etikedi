import CifarService from "@/api/CifarService";

export const nextSample = ({dispatch, commit}: any) => {
    commit("nextCifarSample");
    dispatch("loadDataset");
};

export const prevSample = ({dispatch, commit}: any) => {
    commit("prevCifarSample");
    dispatch("loadDataset");
};

export const loadDataset = ({commit, state}: any) => {
    console.log("Loading current Cifar " + state.cifarId);
    commit("startLoading", null, {root: true}); // calls in root store, loading handled globally
    return CifarService.getCifar({cifarId: state.cifarId}).then(({data}) => {
        commit("setCifarSample", data);
        commit("endLoading", null, {root: true}); // calls in root store, loading handled globally
    });
};

export const labelSample = ({commit}: any, label: string) => {
    const selection = window.getSelection();

    // window.console.log(label);
    // window.console.log(selection);
    function findFeatureId(
        target: Node | null | undefined
    ): HTMLElement | null | undefined {
        let derivedTarget: HTMLElement | null | undefined;

        if (target?.nodeType != 1) {
            derivedTarget = target?.parentElement;
        } else {
            derivedTarget = target as HTMLElement;
        }

        while (derivedTarget && !derivedTarget.hasAttribute("feature_id")) {
            derivedTarget = derivedTarget?.parentElement;
            window.console.log(derivedTarget);
        }

        return derivedTarget;
    }

    let startId = Number(
        findFeatureId(selection?.anchorNode)?.getAttribute("feature_id")
    );
    let endId = Number(
        findFeatureId(selection?.focusNode)?.getAttribute("feature_id")
    );

    // window.console.log(startId);
    // window.console.log("end" + endId);
    if (startId > endId) {
        const temp = startId;
        startId = endId;
        endId = temp;
    }
    // window.console.log("start" + startId);
    // window.console.log("end" + endId);

    commit("changeLabel", {startId, endId, label});
    window.getSelection()?.removeAllRanges();
};
