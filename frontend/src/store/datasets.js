import { writable } from 'svelte/store'
import axios from 'axios'

export const data = writable([])

export async function load() {
  const { data: d } = await axios({
    method: 'get',
    url: '/api/datasets/',
  })
  data.set(d)
}
