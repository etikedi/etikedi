import { writable } from 'svelte/store'
import axios from 'axios'

export enum UserRole {
  Admin = 'admin',
  Worker = 'Worker',
}

export type User = {
  id: number
  email: string
  username: string
  fullname: string
  is_active: boolean
  roles: UserRole
}

export type UserCreated = User & { new_password: string }

export type UserWithoutID = Omit<User, 'id'>

export const data = writable<User[]>([])
export const loading = writable(null)

export async function load() {
  try {
    loading.set(true)
    const { data: d } = await axios({
      method: 'get',
      url: '/users',
    })
    data.set(d.sort((a, b) => b.is_active - a.is_active))
  } finally {
    loading.set(false)
  }
}

export async function add(user: UserWithoutID): Promise<string> {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: '/users',
      method: 'post',
      data: user,
    })
    await load()
    return d.new_password
  } finally {
    loading.set(false)
  }
}

export async function update(id: number | string, user: UserWithoutID) {
  try {
    loading.set(true)
    await axios({
      url: `/users/${id}`,
      method: 'put',
      data: user,
    })
    await load()
  } finally {
    loading.set(false)
  }
}

export async function generateNewPassword(id: number | string): Promise<string> {
  const { data: d } = await axios({
    url: `/users/${id}/reset_password`,
    method: 'post',
  })
  return d.new_password
}

export function empty(): UserWithoutID {
  return {
    email: '',
    fullname: '',
    is_active: true,
    roles: UserRole.Worker,
    username: '',
  }
}
