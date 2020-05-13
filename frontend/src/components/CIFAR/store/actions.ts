import CifarService from "@/api/CifarService";

export const loadCifarSample = ({commit, state}: any) => {
    commit("startLoading");
    return CifarService.getSample({sampleID: state.cifarSampleID}).then(
        ({sample}) => {
            commit("setCifarSample", sample);
            commit("endLoading");
        }
    );
};

export const loadCifarLabels = ({commit, state}: any) => {
    commit("startLoading");
    return CifarService.getLabels({datasetID: state.currentDataset}).then(
        ({labels}) => {
            commit("setCifarLabels", labels);
            commit("endLoading");
        }
    );
};

export const labelCifarSample = ({commit, state, sampleID, label}: any) => {
    commit("startLoading");
    return CifarService.labelSample({
        sampleID: sampleID,
        labelID: label,
        userID: "Hick"
    }).then(({labels}: any) => {
        commit("setCifarLabels", labels);
        commit("endLoading");
    });
};

/*
export const loadImage = ({commit}: any) => {
    commit("startLoading");
    return CifarService.getImage().then(({data}) => {
        const urlCreator = window.URL || window.webkitURL;
        const imageUrl = urlCreator.createObjectURL(data);
        commit("setImage", imageUrl);
        commit("endLoading");
    });
};
*/
