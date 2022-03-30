import { writable } from 'svelte/store'
import axios from 'axios'

export type BattleConfig = {
  QUERY_STRATEGY:
    | 'QueryInstanceBMDR'
    | 'QueryInstanceGraphDensity'
    | 'QueryInstanceLAL'
    | 'QueryInstanceQBC'
    | 'QueryInstanceQUIRE'
    | 'QueryInstanceSPAL'
    | 'QueryInstanceUncertainty'
    | 'QueryInstanceRandom'
    | 'QueryExpectedErrorReduction'
  AL_MODEL: 'DecisionTreeClassifier' | 'RandomForestClassifier' | 'LogisticRegression'
  STOPPING_CRITERIA_Value: number
  STOPPING_CRITERIA: 'all_labeled' | 'num_of_queries' | 'cost_limit' | 'percent_of_unlabel'
  BATCH_SIZE: number
  QUERY_STRATEGY_CONFIG: {
    beta: number
    cls_est: number
    disagreement: 'vote_entropy' | 'KL_divergence'
    gamma: number
    lambda_init: number
    lambda_pace: number
    measure: 'least_confident'
    margin
    entrop
    distance_to_boundar
    method: 'query_by_bagging'
    metric:
      | 'euclidean'
      | 'l2'
      | 'l1'
      | 'manhattan'
      | 'cityblock'
      | 'braycurtis'
      | 'canberra'
      | 'chebyshev'
      | 'correlation'
      | 'cosine'
      | 'dice'
      | 'hamming'
      | 'jaccard'
      | 'kulsinski'
      | 'mahalanobis'
      | 'matching'
      | 'minkowski'
      | 'rogerstanimoto'
      | 'russellrao'
      | 'seuclidean'
      | 'sokalmichener'
      | 'sokalsneath'
      | 'sqeuclidean'
      | 'yule'
      | 'wminkowski'
    mode: 'LAL_iterative' | 'LAL_independent'
    mu: number
    rho: number
    train_slt: boolean
  }
}

export type Diagrams = {
  data_map: any
  uncertainty: any
  class_boundaries: any
  vector_space: any
}

export type Metric = {
  samples: any[]
  performance: number
  time: number
}
export interface MetricData {
  [iteration: number]: {
    process_1: Metric
    process_2: Metric
  }
}
export interface DiagramData {
  process_1: Diagrams
  process_2: Diagrams
}

/**
 * true if both finished
 * false if no data available
 * time in seconds if at least one is finished
 */
export const isFinished = writable<boolean | number>(false)
export const diagrams = writable<any>(null)
export const metricData = writable<any>(null)
export const finishedExperiments = writable<any>(null)
export const loading = writable(null)
export const valid_strategies = writable(null)

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
    localStorage.setItem(`battle-on-dataset-${dataset_id}`, success)
    return success
  } catch {
    return false
  } finally {
    loading.set(false)
  }
}

export async function getStatus(experiment_id: number | string) {
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
     * isFinished {
     *    code: 0 | 1 | 2
     *    time: float | null
     * }
     */
    isFinished.set(status.code == 1 && status.time != null ? status.time : status.code == 2)
    if (status.code === 2) localStorage.removeItem(`experiment-${experiment_id}-running`)
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
    // localStorage.setItem(`battle-${dataset_id}-diagrams`, JSON.stringify(d))
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
