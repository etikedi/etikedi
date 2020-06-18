import axios from "axios";

const api = axios.create({
        //baseURL: 'http://25.93.150.69:5000/api/',
        baseURL: "http://127.0.0.1:5000/api",
        withCredentials: false,
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
        }
    });

export default {
    getAllDatasets(): Promise<any> {
        return api.get("/datasets");
    },

    getLabels({datasetId}): Promise<any> {
        return api.get("/dataset/" + params.datasetId + "/labels");
    },

    getSampleById({sampleId}): Promise<any> {
        return api.get("/sample/" + params.sampleId);
    },
    
    getNextSample({datasetId}): Promise<any> {
        return api.get("/dataset/" + params.datasetId)
    },

    labelSample({
        sampleId,
        labelId,
        userId,
    }): Promise<any> {
        return api.post("/sample/" + params.sampleId, {
            association: {
                "label_id": params.labelId,
                "user_id": params.userId
            }
        });
    }
};
