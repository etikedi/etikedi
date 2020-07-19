import {authService} from "@/api/AuthService";

export const login = ({dispatch, commit}, {username, password, router}) => {
    commit("loginRequest", {username});
    authService.login(username, password).then(
        data => {
            commit("loginSuccess", data);
            router.push("/home");
            location.reload(true);
        },
        error => commit("loginFailure", error)
    );
};
export const logout = ({commit}) => {
    authService.logout();
    commit("logout");
};
