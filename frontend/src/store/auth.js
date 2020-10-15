import { writable } from 'svelte/store'
import axios from 'axios'
import JWTDecode from 'jwt-decode'

axios.defaults.baseURL = 'http://localhost:5000/'
axios.defaults.headers['Accept'] = 'application/json'
axios.defaults.headers['Content-Type'] = 'application/json'
axios.defaults.withCredentials = false

const STORAGE_KEY = 'aergia:token'

export const token = writable(null)

function save(tkn, persist = true) {
  token.set(tkn)
  axios.defaults.headers['Authorization'] = `Bearer ${tkn}`
  if (persist) window.localStorage.setItem(STORAGE_KEY, tkn)
}

function load() {
  const saved = window.localStorage.getItem(STORAGE_KEY)
  if (saved) {
    const decoded = JWTDecode(saved)
    if (decoded.exp > ((Date.now() / 1000) | 0)) {
      save(saved, false)
      return
    }
  }
  save('', false)
}

export async function login(form) {
  // Load from localstorage
  if (!form) {
    load()
    return
  }

  // Load remotely
  const { data } = await axios({
    url: '/login',
    method: 'post',
    data: form,
  })
  save(data.access_token)
}

export function logout(){
  window.localStorage.removeItem(STORAGE_KEY)
  token.set(null)
}