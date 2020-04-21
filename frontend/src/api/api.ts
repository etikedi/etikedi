import axios from 'axios'

export default() => {
    return axios.create({
        //baseURL: 'http://25.93.150.69:5000/api/',
        baseURL: 'http://127.0.0.1:5000/api',
        withCredentials: false,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
}
