import Api from "@/api/api";

export default {
    loadALParams(params : number): Promise<any> {
        //return Api().get("/datasets/" + params + "/config");
        const obj = {
            "CLASSIFIER": "DT",
            "RANDOM_SEED": 23,
            "TEST_FRACTION": 0.6,
            "SAMPLING": "random",
            "CLUSTER": "dummy",
            "NR_LEARNING_ITERATIONS": 1337,
            "NR_QUERIES_PER_ITERATION": 50,
            "USER_QUERY_BUDGET_LIMIT": 17,
            "STOPPING_CRITERIA_UNCERTAINTY": 0.1,
            "STOPPING_CRITERIA_STD": 0.1,
            "STOPPING_CRITERIA_ACC": 0.1,
            "MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS": 0.1,
            "WITH_UNCERTAINTY_RECOMMENDATION": true,
            "UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD": 0.99,
            "UNCERTAINTY_RECOMMENDATION_RATIO": 0.1,
            "WITH_CLUSTER_RECOMMENDATION": true,
            "CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE": 0.6,
            "CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED": 0.7,
            "ALLOW_RECOMMENDATIONS_AFTER_STOP": true,
            "WITH_SNUBA_LITE": true,
            "SNUBA_LITE_MINIMUM_HEURISTIC_ACCURACY": 0.5,
        };
        return Promise.resolve(JSON.stringify(obj));
    },

    submitALParams(params: {
        datasetID: number, 
        value: string
    }): Promise<any> {
        return Api().post("/datasets/" + params.datasetID + "/config", {
            association: {
                "label_id": params.value,
                "user_id": params.datasetID
            }
        });
    },

    getAllDatasets(): Promise<any> {
        // return Api().get("/datasets");
        return new Promise(resolve => {
            resolve({
                datasets: [
                    {
                        id: 27138,
                        name: "DWTC"
                    },
                    {
                        id: 45632,
                        name: "CIFAR"
                    },
                    {
                        id: 13337,
                        name: "ALParams"
                    }
                ]
            });
        });
    },

};