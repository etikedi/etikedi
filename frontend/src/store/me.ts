import { writable, derived } from 'svelte/store'
import axios from 'axios'

export const data = writable(null)

export const isAdmin = derived(data, (data) => data && data.roles === 'admin')

export async function load() {
  const { data: d } = await axios({
    method: 'get',
    url: '/users/me',
  })
  data.set(d)
}
