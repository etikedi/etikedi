import { writable } from 'svelte/store'
import axios from 'axios'

export const DATASET_TYPES = ['table', 'image', 'text']

export const data = writable({})
export const users = writable([])

export async function load() {
  const { data: d } = await axios({
    method: 'get',
    url: '/datasets'
  })
  const obj = d.reduce((acc, cur) => ({ ...acc, [cur.id]: cur }), {})
  data.set(obj)

  const { data: u } = await axios({
    method: 'get',
    url: '/users'
  })
  // const obj = d.reduce((acc, cur) => ({ ...acc, [cur.id]: cur }), {})
  users.set(u)
}