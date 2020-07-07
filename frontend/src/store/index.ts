/* eslint-disable camelcase */
/* eslint-disable @typescript-eslint/camelcase */

import Vue from "vue";
import Vuex from "vuex";
import * as getters from "./getters";
import * as actions from "./actions";
import * as mutations from "./mutations";
import {State} from "./models";

import {defaultApiStore} from "./default/module";

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== "production";

const state: State = {
	// Note: datasetType is no longer set in State, as only the LabelView needs to know about it
	
    // Which API to use to perform requests.
    // Actions from header buttons are delegated to the active
    // apiType. For most datasets in AERGIA, the 'default' apiType
    // will be used, which calls the AergiaDefaultApiService
    // -!- apiType has moved to a getter, which retrieves it from activeDataset
    
    // Available datasets (retrieved from server)
    // datasetId: {name:"bla"}
    datasets: {},
    // currently active dataset ID
    activeDatasetId: null,
    // currently active dataset, updated by 'updateActiveDataset' action!
    activeDataset: null,
    // labels for the active dataset
    labels: [],

    loading: false,
};

const store = new Vuex.Store({
    state,
    modules: {
		//api_<apiType>
        api_default: defaultApiStore,
    },
    getters,
    actions,
    mutations,
    strict: debug
});

if (module.hot) {
    module.hot.accept(["./getters", "./actions", "./mutations"], () => {
        store.hotUpdate({
            getters: require("./getters"),
            actions: require("./actions"),
            mutations: require("./mutations")
        });
    });
}

export default store;
