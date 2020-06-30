import * as actions from "./actions";
import * as mutations from "./mutations";

const debug = process.env.NODE_ENV !== "production";

const user = JSON.parse(localStorage.getItem("user"));
const state = user
    ? {status: {loggedIn: true}, user}
    : {status: {}, user: null};

export const loginStore = {
    state,
    actions,
    mutations,
    modules: {},
    strict: debug,
    namespaced: true // Important! else these will conflict with the root store! see https://vuex.vuejs.org/guide/modules.html
};
