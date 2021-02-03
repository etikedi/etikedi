import { writable } from 'svelte/store'
import axios from 'axios'

export const loading = writable(null)

export async function get(id: number | string) {
  try {
    loading.set(true)
    const { data } = await axios({
      method: 'get',
      url: `/datasets/${id}/config/`,
    })
    return data
  } finally {
    loading.set(false)
  }
}

export async function save(id: number | string, data: any) {
  try {
    loading.set(true)
    await axios({
      method: 'post',
      url: `/datasets/${id}/config/`,
      data,
    })
  } finally {
    loading.set(false)
  }
}
