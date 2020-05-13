import CifarService from "@/api/CifarService";

export const loadAllDatasets = ({commit}: any) => {
    commit("startLoading");
    return CifarService.getAllDatasets().then(({datasets}) => {
        commit("setAllDatasets", datasets);
        commit("endLoading");
    });
};

export const setDataset = ({commit, state}: any, dataset: string) => {
    commit("setCurrentDataset", dataset);
    if (dataset === "CIFAR") {
        commit("startLoading");
        return CifarService.getSampleID({datasetID: state.currentDataset}).then(
            ({sampleID}) => {
                commit("setCifarSampleID", sampleID);
                commit("endLoading");
            }
        );
    }
};

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

export const labelCifarSample = (
    {commit, state}: any,
    sampleID: any,
    label: any
) => {
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
