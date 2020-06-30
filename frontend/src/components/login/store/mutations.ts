export const loginRequest = (state, user) => {
    state.status = {loggingIn: true};
    state.user = user;
};

export const loginSuccess = (state, user) => {
    state.status = {loggedIn: true};
    state.user = user;
};

export const loginFailure = state => {
    state.status = {};
    state.user = null;
};

export const logout = state => {
    state.status = {};
    state.user = null;
};
