<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { getExperiment } from '../../../../store/al-war'
  import Card from '../../../../ui/Card.svelte'

  const dispatch = createEventDispatcher()

  export let accordingBattles

  async function loadBattle(experiment_id: number | string, config: object) {
    dispatch('loadBattle', { experiment_id, config })
  }
</script>

<div class="grid">
  {#each accordingBattles as battle}
    <div>
      <Card>
        <div style="position: relative">
          <h3>Battle ID: <b>{battle['battle_id']}</b></h3>

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

          <ion-icon
            class="play"
            name="play-circle-sharp"
            on:click={() => loadBattle(battle['battle_id'], battle['config'])}
          />
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
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    column-gap: 30px;
    row-gap: 20px;
  }

  ion-icon.play {
    font-size: 3rem;
    color: var(--clr-primary);
    position: absolute;
    top: 0;
    right: 0;
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
