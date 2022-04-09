<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { finishedExperiments, getExperiment } from '../../../../store/al-war'
  import Card from '../../../../ui/Card.svelte'

  const dispatch = createEventDispatcher()

  export let dataset_id

  let accordingBattles = []

  $: if ($finishedExperiments)
    accordingBattles = Object.entries($finishedExperiments).filter((el) => el[1]['dataset_id'] == dataset_id)

  async function loadBattle(experiment_id: number | string, config: object) {
    await getExperiment(experiment_id)
    dispatch('battleLoaded', { experiment_id, config: config['config'] })
  }
</script>

<div class="flex flex-wrap">
  {#each accordingBattles as [experiment_id, config]}
    <div class="fl w-25 card">
      <Card>
        <div style="position: relative">
          <h3>Battle ID: <b>{experiment_id}</b></h3>
          <div class="row">
            <span class="label">Dataset ID:</span>
            <span>{config['dataset_id']}</span>
          </div>
          <h4>Process 1:</h4>
          <div class="row">
            <div class="fl w-third pa2 label">Query Strategy:</div>
            <span class="fl w-two-thirds pa2">{config['config']['exp_configs'][0]['QUERY_STRATEGY']}</span>
          </div>
          <div class="row">
            <div class="fl w-third pa2 label">AL Model:</div>
            <span class="fl w-two-thirds pa2">{config['config']['exp_configs'][0]['AL_MODEL']}</span>
          </div>

          <h4>Process 2:</h4>
          <div class="row">
            <div class="fl w-third pa2 label">Query Strategy:</div>
            <span class="fl w-two-thirds pa2">{config['config']['exp_configs'][1]['QUERY_STRATEGY']}</span>
          </div>
          <div class="row">
            <div class="fl w-third pa2 label">AL Model:</div>
            <span class="fl w-two-thirds pa2">{config['config']['exp_configs'][1]['AL_MODEL']}</span>
          </div>
          <ion-icon class="play" name="play-circle-sharp" on:click={() => loadBattle(experiment_id, config)} />
        </div>
      </Card>
    </div>
  {:else}
    no items
  {/each}
</div>

<style>
  .row {
    display: flex;
    flex-direction: row;
    column-gap: 10px;
    overflow: auto;
  }
  .label {
    color: #555;
  }

  .flex {
    column-gap: 20px;
  }

  ion-icon.play {
    font-size: 3rem;
    color: var(--clr-primary);
    position: absolute;
    top: 0;
    right: 0;
  }
</style>
