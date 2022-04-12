<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { Moon } from 'svelte-loading-spinners'
  import { router } from 'tinro'
  import {
    currentlyViewing,
    finishedExperiments,
    getDiagrams,
    getExperiment,
    getFinishedExperiments,
    getMetrics,
    getRunningExperiments,
    runningExperiments,
  } from '../../../../store/al-war'
  import { data as datasets } from '../../../../store/datasets'
  import Button from '../../../../ui/Button.svelte'
  import Persisted from '../../components/battle/Persisted.svelte'
  import Running from '../../components/battle/Running.svelte'

  let { id } = router.params(),
    accordingFinishedBattles = [],
    accordingRunningBattles = [],
    loading = false,
    runningReady = false,
    persistedReady = false

  $: dataset = $datasets[id]

  getFinishedExperiments()
  getRunningExperiments()

  $: if ($finishedExperiments) {
    accordingFinishedBattles = Object.keys($finishedExperiments)
      .filter((key) => $finishedExperiments[key]['dataset_id'] == id)
      .map((key) => {
        return { ...$finishedExperiments[key], battle_id: key }
      })
    persistedReady = true
  }

  $: if ($runningExperiments && $runningExperiments[id]) {
    accordingRunningBattles = []
    for (const obj of $runningExperiments[id]) {
      console.debug(obj)
      Object.values(obj).map((battle) => {
        accordingRunningBattles.push({
          battle_id: battle['experiment_id'],
          config: battle['config'],
          status: battle['status'],
        })
      })
    }
    accordingRunningBattles = [...accordingRunningBattles]
    runningReady = true
  } else if (typeof $finishedExperiments === 'object') {
    accordingRunningBattles = []
    runningReady = true
  }

  async function loadExperiment(experiment_id, config) {
    loading = true
    try {
      await getExperiment(experiment_id)
      await Promise.all([getMetrics(experiment_id), getDiagrams(experiment_id)])
      $currentlyViewing['config'] = config
      $currentlyViewing['dataset_name'] = dataset.name
      router.goto('./result')
    } catch (e) {
      notifier.danger(e)
    } finally {
      loading = false
    }
  }
</script>

{#if dataset}
  <div>
    <h1>Battle Dashboard</h1>
    <Button style="height: 50%" on:click={() => router.goto('./new')}>Start new battle</Button>
  </div>
  {#if persistedReady && runningReady}
    {#if !loading && (accordingFinishedBattles.length > 0 || accordingRunningBattles.length > 0)}
      {#if accordingFinishedBattles && accordingFinishedBattles.length > 0}
        <h2>Persisted Experiments</h2>
        <Persisted
          bind:accordingBattles={accordingFinishedBattles}
          on:loadBattle={async (e) => await loadExperiment(e.detail['experiment_id'], e.detail['config'])}
        />
      {/if}
      {#if accordingRunningBattles && accordingRunningBattles.length > 0}
        <h2>Running Experiments</h2>
        <Running dataset_id={id} bind:accordingBattles={accordingRunningBattles} />
      {/if}
    {:else if loading}
      <div class="starting">
        Loading persisted data ...
        <Moon size="30" color="#002557" unit="px" duration="1s" />
      </div>
    {:else}
      <div class="display:none">
        {router.goto('./new')}
      </div>
    {/if}
  {/if}
{:else}
  Loading...
{/if}

<style>
  div {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .starting {
    width: 300px;
    display: flex;
    flex-direction: row;
    align-self: center;
    column-gap: 10px;
  }
</style>
