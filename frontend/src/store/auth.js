import { writable } from 'svelte/store'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:5000/'

const STORAGE_KEY = 'aergia:token'

export const auth = writable({
  token: null,
})

function save(token, persist = true) {
  auth.update((auth) => ({ ...auth, token }))
  window.localStorage.setItem(STORAGE_KEY, token)
}

function load() {
  const saved = window.localStorage.getItem(STORAGE_KEY)
  if (saved) save(saved, false)
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
