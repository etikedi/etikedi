import * as getters from "./getters";
import * as actions from "./actions";
import * as mutations from "./mutations";
import {State} from "./models";

const debug = process.env.NODE_ENV !== "production";

const state: State = {
    currentSampleId:"", // currently loaded sample
    samples: [], // sample history, a list of all sample ids. Navigable by clicking next/prev buttons
    currentSampleIndex = 0, // index in samples table. If at end of list, and next button is clicked,
    // calls getNextSample() from API and inserts new ID into samples table
    
    currentSample: {}, // the JSON object of the current sample
};

export const defaultApiStore = {
    state,
    getters,
    actions,
    mutations,
    modules: {},
    strict: debug,
    namespaced: true // Important! else these will conflict with the root store! see https://vuex.vuejs.org/guide/modules.html
};
