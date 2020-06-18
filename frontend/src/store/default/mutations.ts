

export const nextSampleIndex = (state: State) => {
	const historyLen = state.samples.length
	if(state.currentSampleIndex <= historyLen) {
		// if index==length, this means a new dataset must be fetched. This happens in the loadSample action.
		state.currentSampleIndex++;
	}
};

export const prevSampleIndex = (state: State) => {
    if(state.currentSampleIndex > 0) {
		state.currentSampleIndex--;
	}
};

// used when loading from sample history
export const setSample = (state: State, {sampleData, sampleIndex}) => {
    const sample = sampleData.datasample;
    
    state.currentSampleIndex = sampleIndex;
    
    if(state.samples[sampleIndex] != sample.id){
		console.log("setSample called with id=" + sample.id + " but it's not the expected sample. Ignoring");
		return;
	}
    
    state.currentSampleId = sample.id;
    state.currentSample = sample.data;
};

// appends this sample to end of samples history, and sets index there
export const appendSample = (state: State, {sampleData}) => {
    const sample = sampleData.datasample;
    
    const historyLen = state.samples.length
    
    state.samples.push(sample.id)
    state.currentSampleIndex = historyLen
    state.currentSampleId = sample.id;
    state.currentSample = sample.data;
};
