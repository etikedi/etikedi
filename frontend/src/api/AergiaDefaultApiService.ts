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
        return api.get("/dataset/" + datasetId + "/labels");
    },

    getSampleById({sampleId}): Promise<any> {
        return api.get("/sample/" + sampleId);
    },
    
    getNextSample({datasetId}): Promise<any> {
        return api.get("/dataset/" + datasetId)
    },

    labelSample({
        sampleId,
        labelId,
        userId,
    }): Promise<any> {
        return api.post("/sample/" + sampleId, {
            association: {
                "label_id": labelId,
                "user_id": userId
            }
        });
    }
};
