import Api from "@/api/api";

export default {
    getAllDatasets(): Promise<any> {
        return Api().get("/dataset");
    },

    getSampleID(params: {datasetID: string}): Promise<any> {
        return Api().get("/dataset/" + params.datasetID);
    },

    getLabels(params: {datasetID: string}): Promise<any> {
        return Api().get("/dataset/" + params.datasetID + "/labels");
    },

    getSample(params: {sampleID: any}): Promise<any> {
        return Api().get("/sample/" + params.sampleID);
    },

    updateSample(params: {
        sampleID: string;
        labelID: any;
        userID: any;
    }): Promise<any> {
        return Api().post("/sample/" + params.sampleID, {
            labelID: params.labelID,
            userID: params.userID
        });
    }
};
