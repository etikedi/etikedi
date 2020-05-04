import CVService from "@/api/CV-Service";
import CifarService from "@/api/CifarService";

export const nextCv = ({dispatch, commit}: any) => {
    commit("nextCv");
    dispatch("loadCv");
};

export const prevCv = ({dispatch, commit}: any) => {
    commit("prevCv");
    dispatch("loadCv");
};

export const loadCv = ({commit, state}: any) => {
    commit("startLoading");
    return CVService.getCv({cvId: state.cvId}).then(({data}) => {
        commit("setCv", data);
        commit("endLoading");
    });
};

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

export const labelCifarSample = ({commit, state}: any, sampleID: any, label: any) => {
    commit("startLoading");
    return CifarService.updateSample({
        sampleID: sampleID,
        labelID: label,
        userID: "Hick"
    }).then(({labels}) => {
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

export const labelThis = ({commit}: any, label: string) => {
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
