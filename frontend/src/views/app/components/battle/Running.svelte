<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { onDestroy } from 'svelte'
  import { Moon } from 'svelte-loading-spinners'
  import { formatTime } from '../../../../lib/human'
  import {
    getFinishedExperiments,
    getRunningExperiments,
    getStatus,
    saveExperiment,
    terminateExperiment,
  } from '../../../../store/al-war'
  import Button from '../../../../ui/Button.svelte'
  import Card from '../../../../ui/Card.svelte'

  export let dataset_id
  export let accordingBattles

  let intervals = {},
    remainingTimes = {}

  $: if (accordingBattles) {
    for (const battle of accordingBattles) {
      if (intervals[battle['battle_id']]) clearInterval(intervals[battle['battle_id']])
      checkStatus(battle['battle_id'])
    }
  }

  async function checkStatus(battle_id) {
    intervals[battle_id] = setInterval(async () => {
      const status = await getStatus(dataset_id, battle_id)
      if (status === null) {
        delete remainingTimes[battle_id]
      } else if (typeof status === 'number') {
        remainingTimes[battle_id] = status.toFixed(2)
      } else if (status === true) {
        clearOneTimer(battle_id)
        await saveExperiment(battle_id)
        notifier.success(`Battle ${battle_id} finished and persisted!`, 5000)
        await terminate(battle_id)
        await getFinishedExperiments()
        await getRunningExperiments()
      } else if (typeof status === 'string') {
        notifier.danger(status)
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

  async function terminate(battle_id, notify?: boolean) {
    await terminateExperiment(dataset_id, battle_id)
    if (notify) notifier.success('The battle was terminated.', 4000)
    clearOneTimer(battle_id)
    await getFinishedExperiments()
    await getRunningExperiments()
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
          {#if remainingTimes[battle['battle_id']]}
            <div><b>Remaining Time: </b>{remainingTimes[battle['battle_id']]} min</div>
          {:else}
            <div><b>Remaining Time: </b>Currently unknown</div>
          {/if}
          <div class="loading">
            <Moon size="30" color="#002557" unit="px" duration="1s" />
            <div on:click={() => terminate(battle['battle_id'], true)}>
              <ion-icon name="close-outline" />
            </div>
          </div>

          <div class="header">
            <span class="color-dot" style="background-color: #4C78A8" />
            <h4>Process 1:</h4>
          </div>
          <div>&#8226; {battle['config']['exp_configs'][0]['QUERY_STRATEGY']}</div>
          <div>&#8226; {battle['config']['exp_configs'][0]['AL_MODEL']}</div>

          <div class="header">
            <span class="color-dot" style="background-color: #F58518" />
            <h4>Process 2:</h4>
          </div>
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

  .header {
    display: flex;
    flex-direction: row;
    align-items: center;
    column-gap: 10px;
  }

  .color-dot {
    height: 10px;
    width: 10px;
    border-radius: 50%;
    display: inline-block;
  }
</style>
