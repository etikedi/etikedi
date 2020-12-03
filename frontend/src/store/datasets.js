import { writable } from 'svelte/store'
import axios from 'axios'

export const datasets = writable([])

export async function load() {
  const { data: d } = await axios({
    method: 'get',
    url: '/datasets/',
  })
  datasets.set(d)
}
