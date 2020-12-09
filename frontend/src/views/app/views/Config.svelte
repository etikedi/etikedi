<script lang="ts">
  import { onMount } from 'svelte'
  import axios from 'axios'
  import { router } from 'tinro'

  import { data } from '../../../store/datasets'
  import ConfigField from '../components/ConfigField.svelte'

  const { id } = router.params()

  let config = null
  let loading = false

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
      url: `/datasets/${id}/config/`,
    })
    config = data
  })

  async function submit() {
    try {
      if (loading) return
      loading = true
      const { data } = await axios({
        method: 'post',
        url: `/datasets/${id}/config/`,
        data: config,
      })
    } finally {
      loading = false
    }
  }

  function back() {
    router.goto('/app')
  }
</script>

<style>
  ion-icon {
    font-size: 1.5em;
  }
</style>

<div>
  <button class="btn btn-action btn-primary" on:click={back}>
    <ion-icon name="arrow-back" />
  </button>
  <br />
  <br />
  {#if dataset && config}
    <h3>Config <i>{dataset.name}</i></h3>
    <form on:submit|preventDefault={submit}>
      {#each Object.entries(spec) as field}
        <ConfigField {field} bind:config disabled={loading} />
      {/each}
      <button type="button" on:click={back} class="btn">Cancel</button>
      <button type="sumbit" class="btn btn-primary" class:loading disabled={loading}>Update</button>
    </form>
  {:else}
    <div class="loading loading-lg" />
  {/if}
</div>
