<script lang="ts">
  import { onMount } from 'svelte'
  import axios from 'axios'
  import { router } from 'tinro'
  import { sentenceCase } from 'change-case'

  import Button from '../../../ui/Button.svelte'
  import Input from '../../../ui/Input.svelte'
  import Checkbox from '../../../ui/Checkbox.svelte'
  import Select from '../../../ui/Select.svelte'

  import { data } from '../../../store/datasets'

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
      await axios({
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

<div>
  <Button icon="arrow-back-sharp" label="Back" on:click={back} />
  <br />
  {#if dataset && config}
    <h2><b>{dataset.name}</b> Config</h2>
    <form on:submit|preventDefault={submit}>
      {#each Object.entries(spec) as [key, { type, ...props }]}
        {#if type === 'number'}
          <Input {type} {...props} bind:value={config[key]} disabled={loading} label={sentenceCase(key)} />
        {:else if Array.isArray(type)}
          <Select label={sentenceCase(key)} bind:value={config[key]} disabled={loading} values={type} />
        {:else if type === 'bool'}
          <Checkbox bind:value={config[key]} disabled={loading} label={sentenceCase(key)} />
        {/if}
      {/each}
      <Button type="button" on:click={back} label="Cancel" />
      <Button type="submit" {loading} disabled={loading} label="Update" icon="save-sharp" />
    </form>
  {:else}
    <div class="loading loading-lg" />
  {/if}
</div>