import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);


const state = {
    count: 0
}

const mutations = {
    increment(state) {
        state.count++;
    }
}

const actions = {}
const getters={}

export default new Vuex.Store({
    state,
    getters,
    actions,
    mutations
})
