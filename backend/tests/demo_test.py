import random
import os

for dataset_id in range(4, 21):
    UNC_FUNCTION = random.choice(["least_confident", "margin", "entropy"])
    LEARNER_MODEL = random.choice(
        [
            "DecisionTreeClassifier",
            "RandomForestClassifier",
            "LogisticRegression",
            "NaiveBayes",
            "SVC",
        ]
    )
    STRAT_B = random.choice(
        [
            "QueryInstanceGraphDensity",
            "QueryInstanceQBC",
            "QueryInstanceRandom",
            "QueryExpectedErrorReduction",
        ]
    )
    hurl_string = "hurl --progress --variable dataset_id={} --variable UNC_FUNCTION={} --variable LEARNER_MODEL={} --variable STRAT_B={} create_demo_data.http".format(
        dataset_id, UNC_FUNCTION, LEARNER_MODEL, STRAT_B
    )
    print(hurl_string)
    os.system(hurl_string)
