<script lang="ts">
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import { sentenceCase } from 'change-case'
  import { notifier } from '@beyonk/svelte-notifications'

  import Button from '../../../ui/Button.svelte'
  import Input from '../../../ui/Input.svelte'
  import Checkbox from '../../../ui/Checkbox.svelte'
  import Select from '../../../ui/Select.svelte'

  import { data, remove, loading as loadingDatasets } from '../../../store/datasets'
  import { get, save, loading as loadingConfig } from '../../../store/config'

  const { id } = router.params()

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
  $: loading = $loadingConfig || $loadingDatasets

  onMount(async () => {
    config = await get(id)
  })

  async function submit() {
    try {
      await save(id, config)
      notifier.success('Saved')
    } catch (e) {
      console.error(e)
      notifier.danger(e.message)
    }
  }

  async function del() {
    try {
      await remove(id)
      notifier.success('Deleted')
      back()
    } catch (e) {
      console.error(e)
      notifier.danger(e.message)
    }
  }

  function back() {
    router.goto('../../')
  }
</script>

<div>
  <Button icon="arrow-back-circle-sharp" label="Back" on:click={back} />
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
      <Button type="submit" {loading} disabled={loading} label="Update" icon="checkmark-circle-sharp" />
    </form>
    <br />
    <Button
      on:click={del}
      danger
      label="Delete dataset and all the trained data"
      icon="remove-circle-sharp"
      {loading}
      disabled={loading}
    />
  {:else}
    <div class="loading loading-lg" />
  {/if}
</div>
