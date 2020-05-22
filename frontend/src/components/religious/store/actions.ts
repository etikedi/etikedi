import RTService from '@/api/ReligiousText-Service';

export const nextDataset = (
    {dispatch, commit}: any
) => {
    commit('nextRT');
    dispatch('loadDataset');
};


export const prevDataset = (
    {dispatch, commit}: any
) => {
    commit('prevRT');
    dispatch('loadDataset');
};

export const loadDataset = (
    {commit, state}: any
) => {
	//console.log("Loading current RT" + state.rtId)
    commit("startLoading", null, { root: true });// calls in root store, loading handled globally
    return RTService.getReligiousText({rtId: state.rtId}).then(function(data) {                     //'({data}) =>'  -->   'function(data)'
        //console.log("Data:", data);
        commit("setRT", data);
        commit("endLoading", null, { root: true });// calls in root store, loading handled globally
    })
};

export const labelDataset = (
    {commit}: any,
    label: string
) => {
    commit('changeLabel', {label});
};