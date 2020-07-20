import * as actions from "./actions";

const debug = process.env.NODE_ENV !== "production";

export const authStore = {
    actions,
    modules: {},
    strict: debug,
    namespaced: true // Important! else these will conflict with the root store! see https://vuex.vuejs.org/guide/modules.html
};
