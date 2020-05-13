export interface State {
    loading: boolean;
    prevButtonDisabled: boolean;
    nextButtonDisabled: boolean;
    displayFeatureTooltips: boolean;
    allDatasets: string[];
    currentDataset: string;
    cifarSampleID: any;
    cifarSample: CifarSample | undefined;
    cifarLabels: any;
}

export interface CifarSample {
    sampleID: any;
    data: any;
    association: any;
    datasetID?: string;
}
