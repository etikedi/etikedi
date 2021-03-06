import { writable } from 'svelte/store'
import axios from 'axios'

export const loading = writable(null)

export async function get(id: number | string) {
  try {
    loading.set(true)
    const { data } = await axios({
      method: 'get',
      url: `/datasets/${id}/labelingfunctions/`,
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
      url: `/datasets/${id}/labelingfunctions/`,
      data,
    })
  } finally {
    loading.set(false)
  }
}

export async function testFunctions(id: number | string, functions: {function_body: string, id: number}[]) {
  try{
    loading.set(true)

    let {data} = await axios({
      method: 'post',
      url: `/datasets/${id}/labelingfunctions/testrun/`,
      data: functions
    })
    return data

  } finally {
    loading.set(false)
  }
}
