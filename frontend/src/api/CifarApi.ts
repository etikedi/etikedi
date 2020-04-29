import axios from "axios";

export default () => {
    return axios.create({
        //baseURL: 'http://25.93.150.69:5000/api/',
        baseURL: "https://picsum.photos",
        withCredentials: false,
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
        }
    });
};
