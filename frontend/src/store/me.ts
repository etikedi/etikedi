import { writable, derived } from 'svelte/store'
import axios from 'axios'

import type { User } from './users'

export const data = writable<User | null>(null)

export const isAdmin = derived(data, (data) => data && data.roles === 'admin')

export async function load() {
  const { data: d } = await axios({
    method: 'get',
    url: '/users/me',
  })
  data.set(d)
}

export async function changePassword(new_password: string) {
  await axios({
    url: `/users/change_password`,
    method: 'post',
    params: { new_password },
  })
}
