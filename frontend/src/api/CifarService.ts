import Api from "@/api/api";

export default {
    getAllDatasets(): Promise<any> {
        // return Api().get("/datasets");
        return new Promise((resolve) => {
            resolve({
                datasets: [
                    {
                        "id": 27138,
                        "name": "DWTC"
                    },
                    {
                        "id": 45632,
                        "name": "CIFAR"
                    }
                ]
            });
        });
    },

    getSampleID(params: {datasetID: string}): Promise<any> {
        return Api().get("/" + params.datasetID);
    },

    getLabels(params: {datasetID: string}): Promise<any> {
        return Api().get("/" + params.datasetID + "/labels");
    },

    getSample(params: {sampleID: any}): Promise<any> {
        return Api().get("/sample/" + params.sampleID);
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
