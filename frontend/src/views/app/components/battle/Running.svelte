<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { onDestroy } from 'svelte'
  import { Moon } from 'svelte-loading-spinners'
  import { formatTime } from '../../../../lib/human'
  import { getFinishedExperiments, getStatus, running, saveExperiment } from '../../../../store/al-war'
  import Card from '../../../../ui/Card.svelte'

  export let dataset_id

  let intervals = {},
    remainingTimes = {}

  $: if ($running[dataset_id]) {
    for (const battle_id of $running[dataset_id]) {
      if (intervals[battle_id]) clearInterval(intervals[battle_id])
      checkStatus(battle_id)
    }
  }

  async function checkStatus(battle_id) {
    intervals[battle_id] = setInterval(async () => {
      const status = await getStatus(dataset_id, battle_id)
      if (typeof status === 'number') {
        remainingTimes[battle_id] = formatTime(status)
      } else if (status === true) {
        clearInterval(intervals[battle_id])
        delete remainingTimes[battle_id]
        await saveExperiment(battle_id)
        notifier.success(`Battle ${battle_id} finished and persisted!`, 5000)
        await getFinishedExperiments()
      } else {
        delete remainingTimes[battle_id]
      }
    }, 3000)
  }

  onDestroy(() => {
    for (const battle_id of Object.keys(intervals)) {
      clearInterval(intervals[battle_id])
      remainingTimes = {}
    }
  })
</script>

<div class="grid">
  {#each $running[dataset_id] as battle_id}
    <div>
      <Card>
        <div style="position: relative">
          <h3>Battle ID: <b>{battle_id}</b></h3>
          <div><b>Remaining Time: </b>{remainingTimes[battle_id] ?? 'Currently unknown'}</div>
          <div class="loading">
            <Moon size="30" color="#002557" unit="px" duration="1s" />
          </div>
        </div>
      </Card>
    </div>
  {:else}
    no items
  {/each}
</div>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    column-gap: 30px;
    row-gap: 20px;
  }

  .loading {
    position: absolute;
    top: 0;
    right: 0;
  }
</style>
