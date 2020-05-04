export interface State {
    cvId: number;
    loading: boolean;
    cv: any;
    prevButtonDisabled: boolean;
    nextButtonDisabled: boolean;
    displayFeatureTooltips: boolean;
    allDatasets: string[];
    currentDataset: string;
    cifarSampleID: any,
    cifarSample: CifarSample | undefined;
    cifarLabels: any;
}

export interface LabelPayload {
    startId: number;
    endId: number;
    label: string;
}

export interface CifarSample {
    sampleID: any;
    data: any;
    association: any;
    datasetID?: string;
}