import { writable } from 'svelte/store'
import axios from 'axios'

export const data = writable([])
export const loading = writable(null)

export async function load() {
  try {
    loading.set(true)
    const { data: d } = await axios({
      method: 'get',
      url: '/users',
    })
    data.set(d)
  } finally {
    loading.set(false)
  }
}
