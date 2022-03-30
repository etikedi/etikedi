import { writable } from 'svelte/store'
import axios from 'axios'

const IntBetween = (min, max) => ({ type: 'number', min, max })
const FloatBetween = (min, max) => ({ type: 'number', min, max, step: 'any' })
const Choice = (choices) => ({ type: choices })

const ZeroToOne = FloatBetween(0, 1)
const OneHalfToOne = FloatBetween(0.5, 1)
const PositiveFloat = FloatBetween(0, undefined)
const LargerNegativeOne = IntBetween(-1, undefined)
const PositiveInt = IntBetween(0, undefined)
const IntBetween0_2000 = IntBetween(0, 2000)
const Bool = { type: 'bool' }

export const GeneralConfig = {
  BATCH_SIZE: { type: 'number', min: 0, default: 5 },
  STOPPING_CRITERIA: {
    type: ['all_labeled', 'num_of_queries', 'percent_of_unlabel', 'cost_limit', 'time_limit'],
    default: 'all_labeled',
  },
  STOPPING_CRITERIA_VALUE: { type: 'number', min: 0 },
}

export const ProcessConfig = {
  AL_MODEL: Choice(['DecisionTreeClassifier', 'RandomForestClassifier', 'LogisticRegression', 'NaiveBayes', 'SVC']),
}

export const ALConfig = {
  QUERY_STRATEGY: Choice([
    'QueryInstanceBMDR',
    'QueryInstanceGraphDensity',
    'QueryInstanceLAL',
    'QueryInstanceQBC',
    'QueryInstanceQUIRE',
    'QueryInstanceSPAL',
    'QueryInstanceUncertainty',
    'QueryInstanceRandom',
    'QueryExpectedErrorReduction',
  ]),
  AL_MODEL: Choice(['DecisionTreeClassifier', 'LinearRegression', 'KMeans']),
  STOPPING_CRITERIA: Choice(['None', 'num_of_queries', 'cost_limit', 'percent_of_unlabel']),
  BATCH_SIZE: PositiveInt,
  COUNTER_UNTIL_NEXT_EVAL: PositiveInt,
  EVALUATION_SIZE: PositiveInt,
  COUNTER_UNTIL_NEXT_MODEL_UPDATE: PositiveInt,
}

export const BattleConfig = {
  QUERY_STRATEGY: Choice([
    'QueryInstanceBMDR',
    'QueryInstanceGraphDensity',
    'QueryInstanceLAL',
    'QueryInstanceQBC',
    'QueryInstanceQUIRE',
    'QueryInstanceSPAL',
    'QueryInstanceUncertainty',
    'QueryInstanceRandom',
    'QueryExpectedErrorReduction',
  ]),
  AL_MODEL: Choice(['DecisionTreeClassifier', 'RandomForestClassifier', 'LogisticRegression']),
  STOPPING_CRITERIA_VALUE: PositiveInt,
  STOPPING_CRITERIA: Choice(['all_labeled', 'num_of_queries', 'cost_limit', 'percent_of_unlabel']),
  BATCH_SIZE: PositiveInt,
}

export const StrategyConfig = {
  beta: PositiveInt,
  cls_est: PositiveInt,
  disagreement: Choice(['vote_entropy', 'KL_divergence']),
  gamma: ZeroToOne,
  lambda_init: ZeroToOne,
  lambda_pace: PositiveFloat,
  measure: Choice(['least_confident', 'margin', 'entrop', 'distance_to_boundar']),
  method: 'query_by_bagging',
  metric: Choice([
    'euclidean',
    'l2',
    'l1',
    'manhattan',
    'cityblock',
    'braycurtis',
    'canberra',
    'chebyshev',
    'correlation',
    'cosine',
    'dice',
    'hamming',
    'jaccard',
    'kulsinski',
    'mahalanobis',
    'matching',
    'minkowski',
    'rogerstanimoto',
    'russellrao',
    'seuclidean',
    'sokalmichener',
    'sokalsneath',
    'sqeuclidean',
    'yule',
    'wminkowski',
  ]),
  mode: Choice(['LAL_iterative', 'LAL_independent']),
  mu: ZeroToOne,
  rho: ZeroToOne,
  train_slt: Bool,
}

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
