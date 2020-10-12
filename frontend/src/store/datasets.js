import { writable } from 'svelte/store'
import axios from 'axios'

export const datasets = writable([])

export async function load() {
  console.log('test')
  // await fetch('http://localhost:5000/api/datasets', {
  //   method: 'GET', // *GET, POST, PUT, DELETE, etc.
  //   redirect: 'follow', // manual, *follow, error
  //   headers: {
  //     Authorization: window.localStorage.getItem('aergia:token'),
  //   },
  // })
  // console.log('done')
  const { data } = await axios({
    method: 'get',
    url: '/api/datasets',
  })
  // console.log(data)
  // todos.set(data)
}
