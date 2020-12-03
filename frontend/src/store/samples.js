import { writable } from 'svelte/store'
import axios from 'axios'

export const data = writable(null)

export async function loadSample(datasetId) {
  const { data: d } = await axios({
    method: 'get',
    url: `/datasets/${datasetId}/first_sample`,
  })
  data.set(d)
}

export async function putLabel(sample_id, label_id) {
  const { data: d } = await axios({
    method: 'post',
    url: `/samples/${sample_id}`,
    data: {
      sample_id,
      label_id,
    },
  })
  data.set(d)
}
