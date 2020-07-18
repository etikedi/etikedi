import axios from "axios";

export default () => {
	//console.log("Axios using JWT: "+localStorage.getItem('jwtToken'))
    return axios.create({
        //baseURL: 'http://25.93.150.69:5000/api/',
        baseURL: "http://127.0.0.1:5000/api",
        withCredentials: false,
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: 'Bearer ' + localStorage.getItem('jwtToken'),
        }
    });
};
