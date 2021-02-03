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

  // Spec for auto generating the config form
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

  const spec = {
    ALLOW_RECOMMENDATIONS_AFTER_STOP: Bool,
    BATCH_MODE: Bool,
    CLASSIFIER: Choice(['RF', 'SVM', 'NB', 'MLP', 'DT']),
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: ZeroToOne,
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: ZeroToOne,
    CLUSTER: Choice(['dummy', 'random', 'MostUncertain_lc', 'MostUncertain_max_margin', 'MostUncertain_entropy']),
    DISTANCE_METRIC: Choice(['euclidean', 'cosine']),
    GENERATE_NOISE: Bool,
    HYPERCUBE: Bool,
    INITIAL_BATCH_SAMPLING_ARG: IntBetween0_2000,
    INITIAL_BATCH_SAMPLING_HYBRID_FURTHEST_LAB: ZeroToOne,
    INITIAL_BATCH_SAMPLING_HYBRID_FURTHEST: ZeroToOne,
    INITIAL_BATCH_SAMPLING_HYBRID_PRED_UNITY: ZeroToOne,
    INITIAL_BATCH_SAMPLING_HYBRID_UNCERT: ZeroToOne,
    INITIAL_BATCH_SAMPLING_METHOD: Choice(['furthest', 'random']),
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: ZeroToOne,
    N_JOBS: LargerNegativeOne,
    NEW_SYNTHETIC_PARAMS: Bool,
    NR_LEARNING_ITERATIONS: PositiveInt,
    NR_QUERIES_PER_ITERATION: PositiveInt,
    PLOT_EVOLUTION: Bool,
    RANDOM_SAMPLE_EVERY: PositiveInt,
    RANDOM_SEED: PositiveInt,
    SAMPLING: Choice(['random', 'uncertainty_lc', 'uncertainty_max_margin', 'uncertainty_entropy']),
    STATE_ARGSECOND_PROBAS: Bool,
    STATE_ARGTHIRD_PROBAS: Bool,
    STATE_DIFF_PROBAS: Bool,
    STATE_DISTANCES_LAB: Bool,
    STATE_DISTANCES_UNLAB: Bool,
    STATE_DISTANCES: Bool,
    STATE_INCLUDE_NR_FEATURES: Bool,
    STATE_PREDICTED_CLASS: Bool,
    STATE_PREDICTED_UNITY: Bool,
    STATE_UNCERTAINTIES: Bool,
    STOP_AFTER_MAXIMUM_ACCURACY_REACHED: Bool,
    STOPPING_CRITERIA_ACC: ZeroToOne,
    STOPPING_CRITERIA_STD: ZeroToOne,
    STOPPING_CRITERIA_UNCERTAINTY: ZeroToOne,
    TEST_FRACTION: ZeroToOne,
    TIMEOUT_FOR_WORKER: PositiveInt,
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: OneHalfToOne,
    UNCERTAINTY_RECOMMENDATION_RATIO: ZeroToOne,
    USER_QUERY_BUDGET_LIMIT: PositiveFloat,
    VARIABLE_DATASET: Bool,
    WITH_CLUSTER_RECOMMENDATION: Bool,
    WITH_SNUBA_LITE: Bool,
    WITH_UNCERTAINTY_RECOMMENDATION: Bool,
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
