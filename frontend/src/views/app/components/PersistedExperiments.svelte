<script lang="ts">
  import { humanize } from '../../../lib/human'
  import Card from '../../../ui/Card.svelte'
  import Button from '../../../ui/Button.svelte'
  import { finishedExperiments } from '../../../store/al-war'
</script>

<h2><b>Persisted Experiments</b></h2>
{#if $finishedExperiments}
  {#each Object.entries($finishedExperiments) as [experiment_id, config]}
    <Card>
      <div>
        <span class="label">Dataset ID:</span>
        <span>{config['dataset_id']}</span>
      </div>
      <div>
        <span class="label">Experiment ID:</span>
        <span>{experiment_id}</span>
      </div>
      <div>
        <span class="label">Process 1:</span>
        <div>
          <span class="label">Query Strategy:</span>
          <span>{config['config']['exp_configs'][0]['QUERY_STRATEGY']}</span>
        </div>
        <div>
          <span class="label">AL Model:</span>
          <span>{config['config']['exp_configs'][0]['AL_MODEL']}</span>
        </div>
      </div>
      <div>
        <span class="label">Process 2:</span>
        <div>
          <span class="label">Query Strategy:</span>
          <span>{config['config']['exp_configs'][1]['QUERY_STRATEGY']}</span>
        </div>
        <div>
          <span class="label">AL Model:</span>
          <span>{config['config']['exp_configs'][1]['AL_MODEL']}</span>
        </div>
      </div>
    </Card>
  {/each}
{/if}

<style>
  div {
    display: flex;
    flex-direction: row;
    column-gap: 10px;
  }
  .label {
    color: #555;
  }
</style>
