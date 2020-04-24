export interface State {
    cvId: number,
    dwtcId: number,
    loading: boolean,
    cv?: any,
    dwtc?: any,
    prevButtonDisabled: boolean,
    nextButtonDisabled: boolean,
    displayFeatureTooltips: boolean,
}

export interface LabelPayload {
    startId: number,
    endId: number,
    label: string
}