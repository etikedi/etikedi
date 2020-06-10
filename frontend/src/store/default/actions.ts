import ApiService from "@/api/AergiaDefaultApiService";

export const nextSample = ({dispatch, commit}: any) => {
    commit("nextSampleIndex");
    dispatch("loadSample");
};

export const prevSample = ({dispatch, commit}: any) => {
    commit("prevSampleIndex");
    dispatch("loadSample");
};

export const loadSample = ({commit, state, rootState}: any) => {
	var index = state.currentSampleIndex;
    console.log("Loading current sample index" + index);
    commit("startLoading", null, {root: true});
    
    // what do we need to fetch? By ID, or by nextSample?
    var historyLen = state.samples.length;
    if(index >= historyLen){
		// fetch by suggestion
		return ApiService.getNextSample({datasetId: rootState.datasetId})
			.then(({data}) => {
				commit("appendSample", {sampleData: data});
				commit("endLoading", null, {root: true});
			});
	}else{
		// fetch by ID
		return ApiService.getSampleById({sampleId: state.samples[index]})
			.then(({data}) => {
				commit("setSample", {sampleData: data, sampleIndex: index});
				commit("endLoading", null, {root: true});
			});
	}
};

export const labelSample = ({commit}: any, labelId) => {
	commit("startLoading", null, {root: true});
	
    return ApiService.labelSample({
			sampleId: state.currentSampleId,
			labelId: labelId,
			userId: "dummy",
		})
			.then(({data}) => {
				commit("nextSample", null, {root: true});
			});
};
