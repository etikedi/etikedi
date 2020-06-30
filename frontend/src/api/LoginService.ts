import Api from "@/api/api";

function logout() {
    // remove user from local storage to log user out
    localStorage.removeItem("user");
}

function handleResponse(response) {
    return response.text().then(text => {
        const data = text && JSON.parse(text);
        if (!response.ok) {
            if (response.status === 401) {
                // auto logout if 401 response returned from api
                logout();
                location.reload(true);
            }

            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
        }

        return data;
    });
}

async function login(username: string, password: string): Promise<any> {
    const response = await Api().post("/login", {username, password});
    const user = await handleResponse(response);
    // login successful if there's a jwt token in the response
    if (user.token) {
        // store user details and jwt token in local storage to keep user logged in between page refreshes
        localStorage.setItem("user", JSON.stringify(user));
    }
    return user;
}

export const userService = {
    login,
    logout
};
