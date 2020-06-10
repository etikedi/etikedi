import Api from "@/api/api";

export default {
    getAllDatasets(): Promise<any> {
        // return Api().get("/datasets");
        return new Promise(resolve => {
            resolve({
                datasets: [
                    {
                        id: 27138,
                        name: "DWTC",
                        datasetType: "dwtc",
                        apiType: "default",
                    },
                    {
                        id: 45632,
                        name: "CIFAR"
                        datasetType: "cifar",
                        apiType: "default",
                    }
                ]
            });
        });
    },

    getLabels(params: {datasetID: string}): Promise<any> {
        return Api().get("/dataset/" + params.datasetID + "/labels");
    },

    getSampleById(params: {sampleID: any}): Promise<any> {
        return Api().get("/sample/" + params.sampleID);
    },
    
    getNextSample(params: {datasetID: string}): Promise<any> {
        return Api().get("/dataset/" + params.datasetID)
    },

    labelSample(params: {
        sampleID: string;
        labelID: any;
        userID: any;
    }): Promise<any> {
        return Api().post("/sample/" + params.sampleID, {
            association: {
                "label_id": params.labelID,
                "user_id": params.userID
            }
        });
    }
};
