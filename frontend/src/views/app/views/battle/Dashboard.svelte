<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { Moon } from 'svelte-loading-spinners'
  import { router } from 'tinro'
  import {
    currentlyViewing,
    finishedExperiments,
    getDiagrams,
    getFinishedExperiments,
    getMetrics,
    running,
  } from '../../../../store/al-war'
  import { data as datasets } from '../../../../store/datasets'
  import Button from '../../../../ui/Button.svelte'
  import Persisted from '../../components/battle/Persisted.svelte'
  import Running from '../../components/battle/Running.svelte'

  let { id } = router.params(),
    accordingFinishedBattles = [],
    loading = false,
    ready = false

  $: dataset = $datasets[id]

  getFinishedExperiments()

  $: if ($finishedExperiments) {
    accordingFinishedBattles = Object.keys($finishedExperiments)
      .filter((key) => $finishedExperiments[key]['dataset_id'] == id)
      .map((key) => {
        return { ...$finishedExperiments[key], battle_id: key }
      })
    ready = true
  }

  async function loadExperiment(experiment_id) {
    loading = true
    try {
      await Promise.all([getMetrics(experiment_id), getDiagrams(experiment_id)])
      router.goto(`./result`)
    } catch (e) {
      notifier.danger(e)
    } finally {
      loading = false
    }
  }

  async function getRunning() {
    /**
     * TODO
     */
  }
</script>

{#if dataset}
  <div>
    <h1>Battle Dashboard</h1>
    <Button style="height: 50%" on:click={() => router.goto('./new')}>Start new battle</Button>
  </div>
  {#if ready}
    {#if accordingFinishedBattles.length > 0 || $running[id]}
      {#if accordingFinishedBattles && accordingFinishedBattles.length > 0 && !loading}
        <h2>Persisted Experiments</h2>
        <Persisted
          accordingBattles={accordingFinishedBattles}
          on:battleLoaded={async (e) => {
            $currentlyViewing['config'] = e.detail['config']
            $currentlyViewing['dataset_name'] = dataset.name
            await loadExperiment(e.detail['experiment_id'])
          }}
        />
      {/if}
      {#if $running && $running[id]}
        <h2>Running Experiments</h2>
        <Running dataset_id={id} />
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
