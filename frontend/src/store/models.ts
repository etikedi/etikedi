export interface State {
    cvId: number,
    loading: boolean,
    cv: any,
    prevButtonDisabled: boolean,
    nextButtonDisabled: boolean,
    displayFeatureTooltips: boolean,
}

export interface LabelPayload {
    startId: number,
    endId: number,
    label: string
}