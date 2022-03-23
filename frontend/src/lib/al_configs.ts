export interface GeneralConfig {
  STOPPING_CRITERIA_VALUE: number
  STOPPING_CRITERIA: 'all_labeled' | 'num_of_queries' | 'percent_of_unlabel' | 'cost_limit' | 'time_limit'
  BATCH_SIZE: number
}

export interface ProcessConfig {
  AL_MODEL: 'DecisionTreeClassifier' | 'RandomForestClassifier' | 'LogisticRegression' | 'NaiveBayes' | 'SVC'
}

export interface MockSchema {
  beta: number
  gamma: number
  rho: number
  kernel: 'linear' | 'poly' | 'rbf'
}

export let MockQuerySchema = {
  measure: "least_confident"
}

export let mockBattleConfig = {
  QUERY_STRATEGY: 'QueryInstanceUncertainty',
  QUERY_STRATEGY_CONFIG: MockQuerySchema,
  AL_MODEL: 'RandomForestClassifier',
}

export let mockSendConfig = {
  exp_configs: [mockBattleConfig, mockBattleConfig],
  STOPPING_CRITERIA_VALUE: undefined,
  STOPPING_CRITERIA: 'all_labeled',
  BATCH_SIZE: 5,
  PLOT_CONFIG: {
    FEATURES: undefined,
  },
}
