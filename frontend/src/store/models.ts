export interface State {
	datasets: any,
    // currently active dataset ID
    activeDatasetId: string,
    // currently active dataset, updated by 'updateActiveDataset' action!
    activeDataset: any,
    // labels for the active dataset
    labels: any,

    loading: boolean,
}

export interface LabelPayload {
    startId: number;
    endId: number;
    label: string;
}
