class FeatureResolver:

    def __init__(self, dataset, features, sample_ids):
        self.dataset = dataset
        self.features = features
        self.sample_ids = sample_ids

    def resolve(self):
        # TODO Features-Resolving
        resolved_features = [self.features[sample_id] for sample_id in self.sample_ids]
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
