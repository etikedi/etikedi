import {userService} from "@/api/LoginService";
import VueRouter from "vue-router";

export const login = ({dispatch, commit}, {username, password}) => {
    commit("loginRequest", {username});

    userService.login(username, password).then(
        user => {
            commit("loginSuccess", user);
            const router = new VueRouter();
            router.push("/");
        },
        error => {
            commit("loginFailure", error);
            // dispatch("alert/error", error, {root: true});
        }
    );
};
export const logout = ({commit}) => {
    userService.logout();
    commit("logout");
};
