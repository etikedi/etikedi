<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { default as SvelteSelect } from 'svelte-select'
  import { notifier } from '@beyonk/svelte-notifications'
  import { ClassificationBoundariesConfig, GeneralConfig, ProcessConfig } from '../../../../lib/config'
  import Button from '../../../../ui/Button.svelte'
  import Select from '../../../../ui/Select.svelte'
  import { valid_strategies, availableFeatures } from '../../../../store/al-war'
  import { data as datasets, getFeatures } from '../../../../store/datasets'
  import Config from '../Config.svelte'

  const dispatch = createEventDispatcher()

  export let id
  export let classBoundConfig
  export let generalConfig
  export let chosenStrategies
  export let strategySchemas
  export let strategyDefinitions
  export let processConfigs
  export let featureConfig

  $: dataset = $datasets[id]

  $: if (dataset) getDatasetFeatures()

  async function getDatasetFeatures() {
    availableFeatures[id] = await getFeatures(id)
  }

  function handleFeatureSelect(e) {
    if (featureConfig && featureConfig.length > 2) {
      featureConfig.pop()
      notifier.danger('Only two features allowed here.', 3000)
    }
  }
</script>

<h2><b>General</b> Config</h2>
<Config alWar strategySchema={GeneralConfig} bind:config={generalConfig} noTitle={true} />
{#if availableFeatures[id] && availableFeatures[id].length > 1}
  <h2><b>Plot</b></h2>
  <div class="multi-select">
    <span>Features</span>
    <SvelteSelect
      bind:value={featureConfig}
      items={availableFeatures[id]}
      isMulti={true}
      placeholder="Default: PCA"
      on:select={handleFeatureSelect}
    />
  </div>
  <Config alWar strategySchema={ClassificationBoundariesConfig} bind:config={classBoundConfig} noTitle={true} />
{/if}
<div class="config-wrapper">
  {#if $valid_strategies}
    <div>
      <h2><b>Process 1</b> Config</h2>
      <Select
        bind:value={chosenStrategies[0]}
        values={Object.keys($valid_strategies)}
        emptyFirst
        label="Query strategy"
      />
      {#if strategySchemas[0]}
        {#key strategySchemas[0]}
          <h2><b>Strategy</b></h2>
          <Config
            bind:config={processConfigs[0]}
            strategySchema={strategySchemas[0]}
            strategyDefinitions={strategyDefinitions[0]}
            alWar
            noTitle={true}
          />
        {/key}
      {/if}
    </div>
    <div>
      <h2><b>Process 2</b> Config</h2>
      <Select
        bind:value={chosenStrategies[1]}
        values={Object.keys($valid_strategies)}
        emptyFirst
        label="Query strategy"
      />
      {#if strategySchemas[1]}
        {#key strategySchemas[1]}
          <h2><b>Strategy</b></h2>
          <Config
            bind:config={processConfigs[1]}
            strategySchema={strategySchemas[1]}
            strategyDefinitions={strategyDefinitions[1]}
            alWar
            noTitle={true}
          />
        {/key}
      {/if}
    </div>
  {/if}
</div>
{#if generalConfig && classBoundConfig && chosenStrategies[0] && chosenStrategies[1]}
  <Button label="Submit" icon="checkmark-circle-sharp" on:click={() => dispatch('submit')} />
{/if}

<style>
  .wrapper {
    display: grid;
    align-items: center;
  }

  .config-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 50px;
  }

  .progress-bar {
    height: 4px;
    width: 100%;
    background-color: lightgray;
  }

  .progress-bar {
    height: 4px;
    width: 0%;
    background-color: lightskyblue;
    transition: width 0.5s ease-in-out;
  }

  .starting {
    display: flex;
    flex-direction: row;
    align-self: center;
    column-gap: 10px;
  }

  .multi-select {
    --border: 2px solid var(--clr-primary-light);
    --borderRadius: var(--round);
    --placeholderColor: var(--clr-primary-light);
    --borderHoverColor: var(--clr-primary-light-alt);
    --borderFocusColor: var(--clr-primary-light-alt);
    --padding: 1em;
    --multiSelectPadding: 4px 35px 4px 16px;
    --placeholderColor: #babec2;
  }
</style>
