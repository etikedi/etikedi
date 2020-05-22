export interface State {
    datasetType: string,
    loading: boolean,
    prevButtonDisabled: boolean,
    nextButtonDisabled: boolean,
    displayFeatureTooltips: boolean,
    displayFeatureTooltipsSwitch: boolean,
    isHomePage: boolean
}

export interface LabelPayload {
    startId: number,
    endId: number,
    label: string
}