export interface State {
    cifarId: number;
    cifarSampleID: any;
    cifarSample: any;
    cifarLabels: any;
}

export interface CifarSample {
    sampleID: any;
    data: any;
    association: any;
}

export interface Association {
    sampleID: string;
    labelID: string;
    userID: string;
}
