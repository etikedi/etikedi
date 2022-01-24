import { writable, derived } from 'svelte/store'
import axios from 'axios'

export type Sample = {
  id: number
  type: string
  content: any
}

export const samples_to_label = writable<Sample[] | null>([])

export async function loadSample(dataset_id): Promise<Sample> {
  const { data: d } = await axios({
    method: 'get',
    url: `/datasets/${dataset_id}/first_sample`,
  })
  return d
}

export async function addLabel(sample_id, label_id) {
  const { data } = await axios({
    method: 'post',
    url: `/samples/${sample_id}`,
    params: {
      label_id,
    },
  })
  return data
}

export async function getSpecificSample(sample_id) {
  const { data: d } = await axios({
    method: 'get',
    url: `/samples/${sample_id}`,
  })
  return d
}
