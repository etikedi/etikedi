import axios from 'axios'
import { get, writable } from 'svelte/store'

export type Diagrams = {
  acc: string
  classification_boundaries: string[][]
  conf: string[][]
  data_maps: string[]
  vector_space: string[][]
}

export type MetricsResponse = {
  iterations: MetricData[][]
  percentage_labeled: number[]
}
export interface MetricData {
  meta: {
    percentage_labeled: number
    sample_ids: number[]
    time: number
  }
  metrics: {
    Acc: number
    AvgDistanceLabeled: number
    AvgDistanceUnLabeled: number
    F1: number
    F1_AUC: number
    Precision: number
    Recall: number
  }
}

export const diagrams = writable<Diagrams>(null)
export const metricData = writable<MetricsResponse>(null)
export const finishedExperiments = writable<any>(null)
export const loading = writable(null)
export const valid_strategies = writable(null)
export const terminate_experiment = writable<boolean>(false)
export const availableFeatures = writable<object>({})
export const currentlyViewing = writable<object>({})

export async function getValidStrategies(dataset_id: number | string) {
  try {
    loading.set(true)
    const { data: strategies } = await axios({
      url: `al-wars/valid_strategies/${dataset_id}`,
      method: 'get',
    })
    if (strategies && strategies['strategies']) valid_strategies.set(strategies['strategies'])
  } finally {
    loading.set(false)
  }
}

export async function startBattle(dataset_id: number | string, battle_config) {
  try {
    loading.set(true)
    const { data: success } = await axios({
      method: 'post',
      url: `al-wars/start`,
      data: { ...battle_config },
      params: { dataset_id },
    })

    /**
     * success = experiment_id
     */
    return success
  } catch {
    return false
  } finally {
    loading.set(false)
  }
}

export async function getStatus(dataset_id: number | string, experiment_id: number | string) {
  try {
    loading.set(true)
    const { data: status } = await axios({
      url: `al-wars/${experiment_id}/status`,
      method: 'get',
    })
    /**
     * Response:
     * IN_SETUP = 0,
     * TRAINING = 1,
     * COMPLETED = 2
     */
    return status.code == 1 && status.time != null ? status.time : status.code == 2
  } finally {
    loading.set(false)
  }
}

export async function getDiagrams(experiment_id: number | string) {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `al-wars/${experiment_id}/diagrams`,
      method: 'get',
    })
    diagrams.set(d)
  } finally {
    loading.set(false)
  }
}

export async function getMetrics(experiment_id: number | string) {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `al-wars/${experiment_id}/metrics`,
      method: 'get',
    })
    metricData.set(d)
  } finally {
    loading.set(false)
  }
}

export async function terminateExperiment(dataset_id: number | string, experiment_id: number | string) {
  try {
    loading.set(true)
    await axios({
      url: `al-wars/${experiment_id}`,
      method: 'delete',
    })
  } finally {
    loading.set(false)
  }
}

export async function getFinishedExperiments() {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `al-wars`,
      method: 'get',
      params: { 'by-dataset': true },
    })
    finishedExperiments.set(d)
  } finally {
    loading.set(false)
  }
}

export async function saveExperiment(experiment_id: number | string) {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `al-wars/persisted/${experiment_id}`,
      method: 'post',
    })
    return d
  } finally {
    loading.set(false)
  }
}

export async function getExperiment(experiment_id: number | string) {
  try {
    loading.set(true)
    const { data: d } = await axios({
      url: `al-wars/persisted/${experiment_id}`,
      method: 'get',
    })
    return d
  } finally {
    loading.set(false)
  }
}
