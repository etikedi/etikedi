<script context="module">
  export function preload(page) {
    return page.params
  }
</script>

<script>
  import axios from 'axios'
  import { onMount } from 'svelte'
  import { goto } from '@sapper/app'

  import { data } from '../../../../store/datasets'
  import ConfigField from '../_components/ConfigField.svelte'

  export let id

  let config = null
  const ZeroToOne = { type: 'number', min: 0, max: 1, step: 'any' }
  const OneHalfToOne = { type: 'number', min: 0.5, max: 1, step: 'any' }
  const PositiveFloat = { type: 'number', min: 0, step: 'any' }
  const LargerNegativeOne = { type: 'number', min: -1 }
  const PositiveInt = { type: 'number', min: 0 }
  const Bool = { type: 'bool' }
  const spec = {
    SAMPLING: { type: ['random', 'uncertainty_lc', 'uncertainty_max_margin', 'uncertainty_entropy'] },
    CLUSTER: { type: ['dummy', 'random', 'MostUncertain_lc', 'MostUncertain_max_margin', 'MostUncertain_entropy'] },
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: ZeroToOne,
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: OneHalfToOne,
    UNCERTAINTY_RECOMMENDATION_RATIO: ZeroToOne,
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: ZeroToOne,
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: ZeroToOne,
    STOPPING_CRITERIA_UNCERTAINTY: ZeroToOne,
    STOPPING_CRITERIA_ACC: ZeroToOne,
    STOPPING_CRITERIA_STD: ZeroToOne,
    USER_QUERY_BUDGET_LIMIT: PositiveFloat,
    N_JOBS: LargerNegativeOne,
    RANDOM_SEED: PositiveInt,
    NR_QUERIES_PER_ITERATION: PositiveInt,
    NR_LEARNING_ITERATIONS: PositiveInt,
    ALLOW_RECOMMENDATIONS_AFTER_STOP: Bool,
    WITH_UNCERTAINTY_RECOMMENDATION: Bool,
    WITH_CLUSTER_RECOMMENDATION: Bool,
    WITH_SNUBA_LITE: Bool,
    RANDOM_SAMPLE_EVERY: PositiveInt,
    TIMEOUT_FOR_WORKER: PositiveInt,
  }

  $: dataset = $data[id]

  onMount(async () => {
    const { data } = await axios({
      method: 'get',
      url: `/datasets/${id}/config`,
    })
    config = data
    console.log(config)
  })

  async function submit() {
    console.log(config)
    const { data } = await axios({
      method: 'post',
      url: `/datasets/${id}/config`,
      data: config,
    })
  }

  function back() {
    goto('/app')
  }
</script>

{#if dataset}
  <div>
    <h1>{dataset.name}</h1>
    <h3>Config</h3>
    {#if config}
      <form on:submit|preventDefault={submit}>
        {#each Object.entries(spec) as field}
          <ConfigField {field} bind:config />
        {/each}
        <button type="button" on:click={back} class="btn">Cancel</button>
        <button type="sumbit" class="btn btn-primary">Update</button>
      </form>
    {/if}
  </div>
{/if}
