<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { onDestroy } from 'svelte'
  import { Moon } from 'svelte-loading-spinners'
  import { formatTime } from '../../../../lib/human'
  import { getFinishedExperiments, getStatus, saveExperiment, terminateExperiment } from '../../../../store/al-war'
  import Button from '../../../../ui/Button.svelte'
  import Card from '../../../../ui/Card.svelte'

  export let dataset_id
  export let accordingBattles

  let intervals = {},
    remainingTimes = {}

  $: if (accordingBattles) {
    console.debug('hallo', accordingBattles)
    for (const battle of accordingBattles) {
      if (intervals[battle['battle_id']]) clearInterval(intervals[battle['battle_id']])
      checkStatus(battle['battle_id'])
    }
  }

  async function checkStatus(battle_id) {
    intervals[battle_id] = setInterval(async () => {
      const status = await getStatus(dataset_id, battle_id)
      if (typeof status === 'number') {
        remainingTimes[battle_id] = formatTime(status)
      } else if (status === true) {
        clearOneTimer(battle_id)
        await saveExperiment(battle_id)
        notifier.success(`Battle ${battle_id} finished and persisted!`, 5000)
        await getFinishedExperiments()
      } else {
        delete remainingTimes[battle_id]
      }
    }, 3000)
  }

  function clearOneTimer(battle_id) {
    clearInterval(intervals[battle_id])
    delete remainingTimes[battle_id]
  }

  function clearAllTimer() {
    for (const battle_id of Object.keys(intervals)) {
      clearInterval(intervals[battle_id])
      remainingTimes = {}
    }
  }

  async function terminate(battle_id) {
    await terminateExperiment(dataset_id, battle_id)
    clearOneTimer(battle_id)
    await getFinishedExperiments()
  }

  onDestroy(() => {
    clearAllTimer()
  })
</script>

<div class="grid">
  {#each accordingBattles as battle}
    <div>
      <Card>
        <div style="position: relative">
          <h3>Battle ID: <b>{battle['battle_id']}</b></h3>
          <div><b>Remaining Time: </b>{battle['status']['time'] ?? 'Currently unknown'}</div>
          <div class="loading">
            <Moon size="30" color="#002557" unit="px" duration="1s" />
            <div on:click={() => terminate(battle['battle_id'])}>
              <ion-icon name="close-outline" />
            </div>
          </div>

          <h4>Process 1:</h4>
          <div>&#8226; {battle['config']['exp_configs'][0]['QUERY_STRATEGY']}</div>
          <div>&#8226; {battle['config']['exp_configs'][0]['AL_MODEL']}</div>

          <h4>Process 2:</h4>
          <div>&#8226; {battle['config']['exp_configs'][1]['QUERY_STRATEGY']}</div>
          <div>&#8226; {battle['config']['exp_configs'][1]['AL_MODEL']}</div>
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
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    column-gap: 30px;
    row-gap: 20px;
  }

  .loading {
    display: flex;
    column-gap: 10px;
    position: absolute;
    top: 0;
    right: 0;
  }

  .loading > div {
    cursor: pointer;
    font-size: 25px;
  }
</style>
