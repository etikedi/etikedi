import { writable } from 'svelte/store'
import axios from 'axios'

export const DATASET_TYPES = ['table', 'image', 'text']
export type DatasetLabel = {
  id: number
  name: string
}
export type Dataset = {
  id: number
  name: string
  labels: DatasetLabel[]
  statistics: {
    total_samples: number
    labelled_samples: number
    features: number
    labels: number
  }
}

export const data = writable<Record<number, Dataset>>({})
export const loading = writable(null)

export async function load() {
  try {
    loading.set(true)
    const { data: d } = await axios({
      method: 'get',
      url: '/datasets',
    })
    const obj = d.reduce((acc, cur) => ({ ...acc, [cur.id]: cur }), {})
    data.set(obj)
  } finally {
    loading.set(false)
  }
}

export async function remove(id: number | string) {
  try {
    loading.set(true)
    await axios({
      method: 'delete',
      url: `/datasets/${id}/`,
    })
    await load()
  } finally {
    loading.set(false)
  }
}

export async function create(fd: FormData) {
  try {
    loading.set(true)
    await axios({
      url: '/datasets',
      method: 'post',
      data: fd,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    await load()
  } finally {
    loading.set(false)
  }
}
