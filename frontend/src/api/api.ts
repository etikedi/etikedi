import axios from "axios";

// param `isAuth` is set to `true` on login action due to the fact that the api refers to "/api/login" but "/login" is the correct endpoint
export default (isAuth = false) => {
    //console.log("Axios using JWT: "+localStorage.getItem('jwtToken'))
    return axios.create({
        //baseURL: 'http://25.93.150.69:5000/api/',
        baseURL: `http://127.0.0.1:5000${isAuth ? "" : "/api"}`,
        withCredentials: false,
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("jwtToken")
        }
    });
};
