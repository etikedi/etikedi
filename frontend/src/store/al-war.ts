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
export const running = writable<object>({})

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

    const currRunning = get(running)
    if (currRunning[dataset_id] && Array.isArray(currRunning[dataset_id])) {
      currRunning[dataset_id].push(success)
    } else {
      currRunning[dataset_id] = [success]
    }
    running.set(currRunning)

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
    const currRunning = get(running)
    if (status.code === 2 && currRunning[dataset_id] && Array.isArray(currRunning[dataset_id])) {
      currRunning[dataset_id].splice(currRunning[dataset_id].indexOf(experiment_id), 1)
      if (currRunning[dataset_id].length === 0) delete currRunning[dataset_id]
    }
    running.set(currRunning)
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

export async function terminateExperiment(experiment_id: number | string) {
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
      url: `al-wars/persisted`,
      method: 'get',
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
