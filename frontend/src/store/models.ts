export interface State {
	apiType: string;
    datasetType: string;
    loading: boolean;
    datasets: any;
}

export interface LabelPayload {
    startId: number;
    endId: number;
    label: string;
}
