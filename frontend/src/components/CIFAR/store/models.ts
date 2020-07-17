export interface State {
    cifarId: number;
    cifar: any;
}
export interface LabelPayload {
    startId: number;
    endId: number;
    label: string;
}

export interface Association {
    sampleID: string;
    labelID: string;
    userID: string;
}
