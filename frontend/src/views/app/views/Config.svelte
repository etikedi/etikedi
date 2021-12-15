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

  export let alWar = false
  export let config = null

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

  const spec_query_strategy = {
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
  {#if !alWar}
    <Button icon="arrow-back-circle-sharp" label="Back" on:click={back} />
  {/if}
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
      {#if !alWar}
        <Button type="submit" {loading} disabled={loading} label="Update" icon="checkmark-circle-sharp" />
      {/if}
    </form>
    <br />
    {#if !alWar}
      <Button
        on:click={del}
        danger
        label="Delete dataset and all the trained data"
        icon="remove-circle-sharp"
        {loading}
        disabled={loading}
      />
    {/if}
  {:else}
    <div class="text-center">
      <div class="loading loading-lg" />
      <p>Waiting for server</p>
    </div>
  {/if}
</div>
