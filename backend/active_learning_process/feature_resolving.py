class FeatureResolver:

    def __init__(self, dataset, features):
        self.dataset = dataset
        self.features = features

    def resolve(self):
        # TODO Features-Resolving
        resolved_features = []
        feature_names = []
        if self.dataset == "cifar":
            pass
        elif self.dataset == "dwtc":
            pass
        elif self.dataset == "religious_texts":
            pass
        elif self.dataset == "equations":
            pass
        return (resolved_features, feature_names)
