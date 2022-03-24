export interface GeneralConfig {
  STOPPING_CRITERIA_VALUE: number
  STOPPING_CRITERIA: 'all_labeled' | 'num_of_queries' | 'percent_of_unlabel' | 'cost_limit' | 'time_limit'
  BATCH_SIZE: number
}

export interface ProcessConfig {
  AL_MODEL: 'DecisionTreeClassifier' | 'RandomForestClassifier' | 'LogisticRegression' | 'NaiveBayes' | 'SVC'
}

export let MockQuerySchema = {
  measure: 'least_confident',
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

export const BMDRConfig = {
  title: 'BMDRConfig',
  type: 'object',
  properties: {
    beta: {
      title: 'Beta',
      default: 1000,
      type: 'number',
    },
    gamma: {
      title: 'Gamma',
      default: 0.1,
      type: 'number',
    },
    rho: {
      title: 'Rho',
      default: 1,
      type: 'number',
    },
    kernel: {
      default: 'rbf',
      allOf: [
        {
          $ref: '#/definitions/QKernel',
        },
      ],
    },
    description: {
      title: 'Description',
      default:
        'https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/huangsj/alipy/page_reference/api_classes/api_query_strategy.query_labels QueryInstanceBMDR.html',
      type: 'string',
    },
  },
  definitions: {
    QKernel: {
      title: 'QKernel',
      description: 'An enumeration.',
      enum: ['linear', 'poly', 'rbf'],
      type: 'string',
    },
  },
}
