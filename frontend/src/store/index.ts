import Vue from "vue"
import Vuex from "vuex"
// Enable again if there is something in getters.ts
// import * as getters from "./getters"
import * as actions from "./actions"
import * as mutations from "./mutations"
import {State} from "@/store/models";

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== "production";

const state: State = {
    cvId: 3,
    loading: false,
    cv: {},
    prevButtonDisabled: false,
    nextButtonDisabled: false,
    displayFeatureTooltips: true,
};

const store = new Vuex.Store({
    state,
    getters: {},
    actions,
    mutations,
    modules: {},
    strict: debug
});

if (module.hot) {
    module.hot.accept([
        "./getters",
        "./actions",
        "./mutations"
    ], () => {
        store.hotUpdate({
            getters: require("./getters"),
            actions: require("./actions"),
            mutations: require("./mutations")
        })
    })
}

export default store
