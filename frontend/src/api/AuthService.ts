import Api from "@/api/api";

function logout() {
    // remove user from local storage to log user out
    localStorage.removeItem("jwtToken");
}

function handleResponse(response) {
    if (response.statusText !== "OK") {
        if (response.status === 401) {
            logout();
            location.reload(true);
        }
        return Promise.reject(response.statusText);
    }

    return response.data;
}

async function login(username: string, password: string): Promise<any> {
    // set param to `true` to solve the login endpoint issue commented in api.ts
    const response = await Api(true).post("/login", {username, password});
    const data = await handleResponse(response);
    // login successful if there's a jwt token in the response
    if (data.access_token) {
        // store user details and jwt token in local storage to keep user logged in between page refreshes
        localStorage.setItem("jwtToken", data.access_token);
    }
    return data;
}

export const authService = {
    login,
    logout
};
