import { writable } from 'svelte/store'
import axios from 'axios'

export const todos = writable([])

export async function fetch() {
  const { data } = await axios.get('https://jsonplaceholder.typicode.com/todos')
  todos.set(data)
}
