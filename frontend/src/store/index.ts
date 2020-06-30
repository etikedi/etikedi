import Vue from "vue";
import Vuex from "vuex";
import * as getters from "./getters";
import * as actions from "./actions";
import * as mutations from "./mutations";
import {State} from "./models";

import {cvStore} from "@/components/CV/store/module";
import {dwtcStore} from "@/components/dwtc/store/module";
import {religiousStore} from "@/components/religious/store/module";
import {cifarStore} from "@/components/CIFAR/store/module";
import {loginStore} from "@/components/login/store/module";

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== "production";

const state: State = {
    datasetType: "cv",

    loading: false,
    prevButtonDisabled: false,
    nextButtonDisabled: false,
    displayFeatureTooltips: true,
    displayFeatureTooltipsSwitch: true,
    isHomePage: true
};

const store = new Vuex.Store({
    state,
    modules: {
        cv: cvStore,
        dwtc: dwtcStore,
        religious: religiousStore,
        cifar: cifarStore,
        login: loginStore
        // add imported dataset type modules here!
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
