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
    })
}

export const labelThis = ({commit}, label) => {
    var selection = "";
    if (window.getSelection) {
        selection = window.getSelection();
    } else if (document.selection && document.selection.type != "Control") {
        selection = document.selection.createRange();
    }

    // parse term ids from selection
    // change state of selected items to reflect the newly selected labels
    var startId = Number(selection.anchorNode.parentElement.parentElement.parentElement.id);
    var endId = Number(selection.focusNode.parentElement.parentElement.parentElement.id);
    window.console.log(label);
    window.console.log(selection);

    window.console.log("start" + startId);
    window.console.log("end" + endId);
    if (startId > endId) {
        let temp = startId;
        startId = endId;
        endId = temp;
    }
    window.console.log("start" + startId);
    window.console.log("end" + endId);


    commit('changeLabel', {startId, endId, label});
    if (window.getSelection) {
        window.getSelection().removeAllRanges();
    }
    else if (document.selection) {
        document.selection.empty();
    }
}
