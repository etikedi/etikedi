

export const sampleShortTitle = function(state){
	return state.currentSampleIndex;
}

export const prevButtonDisabled = function(state){
	return state.currentSampleIndex <= 0;
}

export const nextButtonDisabled = function(state){
	return false;
}
