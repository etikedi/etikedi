import Api from "@/api/api";

export default {
    loadALParams(datasetID : number): Promise<any> {
        return Api().get("/datasets/" + datasetID + "/config");
    },

    submitALParams(params: {
        datasetID: number, 
        paramString: string
    }): Promise<any> {
        return Api().post("/datasets/" + params.datasetID + "/config", {
            string: params.paramString,
        });
    },

};