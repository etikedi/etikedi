import CV_service from '@/api/CV_Service';

export const nextCv = ({dispatch, commit}) => {
    commit('nextCv');
    dispatch('loadCv');
}


export const prevCv = ({dispatch, commit}) => {
    commit('prevCv');
    dispatch('loadCv');
}

export const loadCv = ({commit, state}) => {
    commit("start_loading");
    return CV_service.getCv({cv_id: state.cv_id}).then(({data}) => {
        commit('setCv', data);
        commit("end_loading");
    })
}

export const labelThis = ({commit}, label) => {
    var selection = "";
    if (window.getSelection) {
        selection = window.getSelection();
    } else if (document.selection && document.selection.type != "Control") {
        selection = document.selection.createRange();
    }

    // window.console.log(label);
    // window.console.log(selection);
    function find_feature_id(target) {
        if (target.nodeType != 1) {
            target = target.parentElement;
        }
        while (!target.hasAttribute("feature_id")) {
            target = target.parentElement;
            window.console.log(target);
        }
        return target;
    }
    var startId = Number(find_feature_id(selection.anchorNode).getAttribute("feature_id"));
    var endId = Number(find_feature_id(selection.focusNode).getAttribute("feature_id"));


    // window.console.log(startId);
    // window.console.log("end" + endId);
    if (startId > endId) {
        let temp = startId;
        startId = endId;
        endId = temp;
    }
    // window.console.log("start" + startId);
    // window.console.log("end" + endId);

    commit('changeLabel', {startId, endId, label});
    if (window.getSelection) {
        window.getSelection().removeAllRanges();
    }
    else if (document.selection) {
        document.selection.empty();
    }
}
