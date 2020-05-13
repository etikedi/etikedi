export interface State {
    datasetType: string,
    loading: boolean,
    prevButtonDisabled: boolean,
    nextButtonDisabled: boolean,
    displayFeatureTooltips: boolean,
}

export interface LabelPayload {
    startId: number,
    endId: number,
    label: string
}
