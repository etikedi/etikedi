import { writable } from 'svelte/store'
import axios from 'axios'

export type BattleConfig = {}
export type Diagram = {}
export type Metrics = {}

export const isFinished = writable<boolean>(true)
export const diagrams = writable<Diagram[]>(null)
export const metrics = writable<Metrics[]>(null)
export const loading = writable(null)

export async function startBattle(dataset_id: number | string, config1: BattleConfig, config2: BattleConfig) {
  try {
    loading.set(true)
    const { data: success } = await axios({
      method: 'post',
      url: `/al-war/${dataset_id}/start`,
      data: { config1, config2 },
    })
    return success
  } finally {
    loading.set(false)
  }
}

export async function getStatus(dataset_id: number | string) {
  try {
    loading.set(true)
    const { data: isFinish } = await axios({
      url: `/al-war/${dataset_id}/is_finish`,
      method: 'get',
    })
    isFinished.set(isFinish)
  } finally {
    loading.set(false)
  }
}

export async function getDiagrams(dataset_id: number | string) {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `/al-war/${dataset_id}/get_diagrams`,
      method: 'get',
    })
    diagrams.set(d)
  } finally {
    loading.set(false)
  }
}

export async function getMetrics(dataset_id: number | string) {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `/al-war/${dataset_id}/get_metrics`,
      method: 'get',
    })
    metrics.set(d)
  } finally {
    loading.set(false)
  }
}
