import Vue from 'vue'
import Vuex from 'vuex'
import * as getters from './getters'
import * as actions from './actions'
import * as mutations from './mutations'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production';

const state = {
    cv_id: 21,
    cv: {
        content: "Loading CV…",
        label: "",
        features: [],
        id: 21
    },
    prevButtonDisabled: false,
    nextButtonDisabled: false,
    // history: []
}

const store = new Vuex.Store({
    state,
    getters,
    actions,
    mutations,
    strict: debug
})

if (module.hot) {
    module.hot.accept([
        './getters',
        './actions',
        './mutations'
    ], () => {
        store.hotUpdate({
            getters: require('./getters'),
            actions: require('./actions'),
            mutations: require('./mutations')
        })
    })
}

export default store
