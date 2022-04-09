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
  } from '../../../../store/al-war'
  import { data as datasets } from '../../../../store/datasets'
  import Button from '../../../../ui/Button.svelte'
  import Persisted from '../../components/battle/Persisted.svelte'

  let { id } = router.params(),
    accordingFinishedBattles = [],
    loading = false

  $: dataset = $datasets[id]

  getFinishedExperiments()

  $: if ($finishedExperiments)
    accordingFinishedBattles = Object.keys($finishedExperiments)
      .filter((key) => $finishedExperiments[key]['dataset_id'] == id)
      .map((key) => {
        return { ...$finishedExperiments[key], battle_id: key }
      })

  async function loadExperiment(experiment_id) {
    loading = true
    try {
      await Promise.all([getMetrics(experiment_id), getDiagrams(experiment_id)])
      console.debug('exp', experiment_id)
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
  <h1>Battle Dashboard</h1>
  {#if accordingFinishedBattles && accordingFinishedBattles.length > 0 && !loading}
    <div>
      <h2>Persisted Experiments</h2>
      <Button style="height: 50%" on:click={() => router.goto('./new')}>Start new battle</Button>
    </div>
    <h3>There are some battles persisted for this dataset. Do you want to review one of them?</h3>
    <Persisted
      dataset_id={id}
      on:battleLoaded={async (e) => {
        $currentlyViewing['config'] = e.detail['config']
        $currentlyViewing['dataset_name'] = dataset.name
        await loadExperiment(e.detail['experiment_id'])
      }}
    />
    <!-- TODO: 
    {#if accordingFinishedBattles && accordingFinishedBattles.length > 0 && !loading}
      <h2>Running Experiments</h2>
    {/if}
    -->
  {:else if loading}
    <div class="starting">
      Loading persisted data ...
      <Moon size="30" color="#002557" unit="px" duration="1s" />
    </div>
  {:else}
    <div class="display:none">
      <!--
      {router.goto('./new')}
      -->
    </div>
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
