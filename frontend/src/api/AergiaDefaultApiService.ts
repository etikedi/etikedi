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

    getLabels(params: {datasetID: string}): Promise<any> {
        return api.get("/dataset/" + params.datasetID + "/labels");
    },

    getSampleById(params: {sampleID: any}): Promise<any> {
        return api.get("/sample/" + params.sampleID);
    },
    
    getNextSample(params: {datasetID: string}): Promise<any> {
        return api.get("/dataset/" + params.datasetID)
    },

    labelSample(params: {
        sampleID: string;
        labelID: any;
        userID: any;
    }): Promise<any> {
        return api.post("/sample/" + params.sampleID, {
            association: {
                "label_id": params.labelID,
                "user_id": params.userID
            }
        });
    }
};
