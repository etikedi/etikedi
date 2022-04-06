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
  RANDOM_SEED: { ...PositiveInt, default: 42 },
  TRAIN_TEST_SPLIT: { ...ZeroToOne, default: 0.3 },
  INITIALLY_LABELED: { ...ZeroToOne, default: 0.05 },
}

export const ClassificationBoundariesConfig = {
  NBR_OF_RANDOM_SAMPLE: { ...PositiveInt, default: 100 },
  MAX_X_BINS: { ...PositiveInt, default: 20 },
  MAX_Y_BINS: { ...PositiveInt, default: 20 },
}

export const ProcessConfig = {
  AL_MODEL: Choice([
    'DecisionTreeClassifier',
    'RandomForestClassifier',
    'LogisticRegression',
    'NaiveBayes',
    'SVC',
    'MLP',
  ]),
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
