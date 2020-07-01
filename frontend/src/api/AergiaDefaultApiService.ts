import api from "./api"

export default {
    getAllDatasets(): Promise<any> {
		console.log("(AergiaDefaultApi) getAllDatasets /datasets/")
        return api().get("/datasets/");
    },

    getLabels({datasetId}): Promise<any> {
		console.log("(AergiaDefaultApi) getLabels /datasets/" + datasetId + "/labels")
        return api().get("/datasets/" + datasetId + "/labels");
    },

    getSampleById({sampleId}): Promise<any> {
		console.log("(AergiaDefaultApi) getSampleById /sample/" + sampleId)
        return api().get("/sample/" + sampleId);
    },
    
    getNextSample({datasetId}): Promise<any> {
		// this doesnt work
		//console.log("(AergiaDefaultApi) getNextSample /datasets/" + datasetId + "/")
        //return api().get("/datasets/" + datasetId + "/")
        console.log("(AergiaDefaultApi) getSampleById /sample/1")
        return api().get("/sample/1");
    },

    labelSample({
        sampleId,
        labelId,
        userId,
    }): Promise<any> {
        console.log("(AergiaDefaultApi) labelSample /sample/" + sampleId)
        return api().post("/sample/" + sampleId, {
            association: {
                "label_id": labelId,
                "user_id": userId
            }
        });
    }
};
