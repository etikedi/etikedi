import Api from "@/api/api";

export default {
    loadALParams(): Promise<any> {
        //return Api().get("/alparams/")
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

    submitALParams(params: string): Promise<any> {
        return Api.post("/alparams/", {
            association: {
                "label_id": params,
                "user_id": params
            }
        });
    }
};