import { writable } from 'svelte/store'
import axios from 'axios'

export const datasets = writable([])

export async function fetch() {
  const { data } = await axios({
    url: '/api/datasets',
    withCredentials: false,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      // Authorization: "Bearer " + localStorage.getItem("jwtToken")
    },
  })
  console.log(data)
  // todos.set(data)
}
