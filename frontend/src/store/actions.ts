import CVService from '@/api/CV-Service';
import RTService from '@/api/ReligiousText-Service';
import { startLoading } from './mutations';

export const nextCv = (
    {dispatch, commit}: any
) => {
    commit('nextCv');
    dispatch('loadCv');
};


export const prevCv = (
    {dispatch, commit}: any
) => {
    commit('prevCv');
    dispatch('loadCv');
};

export const loadCv = (
    {commit, state}: any
) => {
    commit("startLoading");
    return CVService.getCv({cvId: state.cvId}).then(({data}) => {
        commit('setCv', data);
        commit("endLoading");
    })
};

export const labelThis = (
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

export const loadRT = (
    {commit, state}: any
) => {
    commit('startLoading');
    console.log("loadRT()");
    return RTService.getReligiousText({rtId: state.rtId}).then(({data}) => {
        console.log('loadingReligiousText()' + data);
        commit('setRT', data);
        commit('endLoading');
    })
};

export const nextRT = (
    {dispatch, commit}: any
) => {
    commit('nextRT');
    dispatch('loadRT');
};


export const prevRT = (
    {dispatch, commit}: any
) => {
    commit('prevRT');
    dispatch('loadRT');
};