export interface State {
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
