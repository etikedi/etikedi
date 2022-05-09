import { writable } from 'svelte/store'
import axios from 'axios'
import JWTDecode from 'jwt-decode'

import { devProdSwitch } from '../lib/utils'
import * as process from 'process';

const productionUrl: string = process.env.PRODUCTION_URL || 'http://localhost:8000/'
axios.defaults.baseURL = devProdSwitch('http://localhost:8000/', productionUrl)
axios.defaults.headers['Accept'] = 'application/json'
axios.defaults.withCredentials = false

const STORAGE_KEY = 'etikedi:token'

export const token = writable(null)

function save(tkn, persist = true) {
  token.set(tkn)
  axios.defaults.headers['Authorization'] = `Bearer ${tkn}`
  if (persist) window.localStorage.setItem(STORAGE_KEY, tkn)
}

function load() {
  const saved = window.localStorage.getItem(STORAGE_KEY)
  try {
    if (saved) {
      const decoded: any = JWTDecode(saved)
      if (decoded.exp > ((Date.now() / 1000) | 0)) {
        save(saved, false)
        return
      }
    }
    save('', false)
  } catch {
    save('', false)
  }
}

export type LoginForm = {
  username: string
  password: string
}
export async function login(form?: LoginForm) {
  // Load token from localstorage if no form is provided
  if (!form) {
    load()
    return
  }

  // Load remotely
  const params = new URLSearchParams(form)
  const { data } = await axios({
    url: '/token',
    method: 'post',
    data: params,
  })
  save(data.access_token, true)
}

export function logout() {
  window.localStorage.removeItem(STORAGE_KEY)
  token.set(false)
}
