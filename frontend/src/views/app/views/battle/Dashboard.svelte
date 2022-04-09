<script lang="ts">
  import Button from '../../../../ui/Button.svelte'
  import Config from '../Config.svelte'
  import { data as datasets, getFeatures } from '../../../../store/datasets'
  import { router } from 'tinro'
  import { onDestroy, getContext } from 'svelte'
  import {
    getStatus,
    isFinished,
    startBattle,
    getMetrics,
    metricData,
    getDiagrams,
    diagrams,
    getValidStrategies,
    valid_strategies,
    terminate_experiment,
    terminateExperiment,
    getFinishedExperiments,
    saveExperiment,
    finishedExperiments,
  } from '../../../../store/al-war'
  import { Moon } from 'svelte-loading-spinners'
  import { notifier } from '@beyonk/svelte-notifications'
  import Result from '../../components/battle/Result.svelte'
  import Popup from '../../components/Modal.svelte'
  import Card from '../../../../ui/Card.svelte'
  import Select from '../../../../ui/Select.svelte'
  import { ClassificationBoundariesConfig, GeneralConfig, ProcessConfig } from '../../../../lib/config'
  import { default as SvelteSelect } from 'svelte-select'
  import Persisted from '../../components/battle/Persisted.svelte'

  let { id } = router.params(),
    accordingFinishedBattles = [],
    experiment_id,
    config

  /**
   * DEV
   */
  $: if ($metricData) console.debug('metrics:', $metricData)
  $: if ($diagrams) console.debug('diagrams:', $diagrams)

  $: dataset = $datasets[id]
  $: if ($finishedExperiments)
    accordingFinishedBattles = Object.keys($finishedExperiments)
      .filter((key) => $finishedExperiments[key]['dataset_id'] == id)
      .map((key) => {
        return { ...$finishedExperiments[key], battle_id: key }
      })

  $: console.debug('according:', accordingFinishedBattles)

  // Get persisted experiments
  getFinishedExperiments()

  async function getData() {
    try {
      await Promise.all([getMetrics(experiment_id), getDiagrams(experiment_id)])
    } catch (e) {
      console.warn('Error while loading data:', e)
    }
  }
</script>

<h1>Battle Dashboard</h1>
{#if accordingFinishedBattles && accordingFinishedBattles.length > 0}
  <div>
    <h2>Persisted Experiments</h2>
    <Button style="height: 50%" on:click={() => {}}>Start new battle</Button>
  </div>
  <h3>There are some battles persisted for this dataset. Do you want to review one of them?</h3>
  <Persisted
    dataset_id={id}
    on:battleLoaded={async (e) => {
      experiment_id = e.detail['experiment_id']
      config = e.detail['config']
      await getData()
    }}
  />
  <h2>Running Experiments</h2>
{:else}
  nothing to show
{/if}

<style>
  div {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
