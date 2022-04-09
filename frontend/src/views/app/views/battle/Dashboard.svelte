<script lang="ts">
  import Button from '../../../../ui/Button.svelte'
  import Config from '../Config.svelte'
  import { data as datasets, getFeatures } from '../../../../store/datasets'
  import { router } from 'tinro'
  import { onDestroy, getContext } from 'svelte'
  import {
    getStatus,
    isFinished,
    startBattle,
    getMetrics,
    metricData,
    getDiagrams,
    diagrams,
    getValidStrategies,
    valid_strategies,
    terminate_experiment,
    terminateExperiment,
    getFinishedExperiments,
    saveExperiment,
    finishedExperiments,
  } from '../../../../store/al-war'
  import { Moon } from 'svelte-loading-spinners'
  import { notifier } from '@beyonk/svelte-notifications'
  import Result from '../../components/battle/Result.svelte'
  import Popup from '../../components/Modal.svelte'
  import Card from '../../../../ui/Card.svelte'
  import Select from '../../../../ui/Select.svelte'
  import { ClassificationBoundariesConfig, GeneralConfig, ProcessConfig } from '../../../../lib/config'
  import { default as SvelteSelect } from 'svelte-select'
  import Persisted from '../../components/battle/Persisted.svelte'

  let showPersisted = true,
    showConfig = true,
    ready,
    dataset,
    training = false,
    remainingTime,
    interval,
    starting = false,
    progressElement,
    chosenStrategies = [],
    generalConfig,
    featureConfig,
    classBoundConfig,
    processConfigs = [{}, {}],
    strategySchemas = [],
    strategyDefinitions = [],
    { open } = getContext('simple-modal'),
    { close } = getContext('simple-modal'),
    { id } = router.params(),
    experiment_id = undefined,
    sendConfig,
    availableFeatures = [],
    accordingFinishedBattles = []

  /**
   * DEV
   */
  $: if ($metricData) console.debug('metrics:', $metricData)
  $: if ($diagrams) console.debug('diagrams:', $diagrams)

  $: dataset = $datasets[id]
  $: ready = dataset && chosenStrategies[0] && chosenStrategies[1]
  $: if (dataset) getDatasetFeatures()
  $: if ($finishedExperiments)
    accordingFinishedBattles = Object.keys($finishedExperiments)
      .filter((key) => $finishedExperiments[key]['dataset_id'] == id)
      .map((key) => {
        return { ...$finishedExperiments[key], battle_id: key }
      })

  $: console.debug('according:', accordingFinishedBattles)

  $: if (chosenStrategies[0]) {
    strategySchemas[0] = {
      ...ProcessConfig,
      ...JSON.parse($valid_strategies[chosenStrategies[0]])['properties'],
    }
    strategyDefinitions[0] = JSON.parse($valid_strategies[chosenStrategies[0]])['definitions']
  }

  $: if (chosenStrategies[1]) {
    strategySchemas[1] = {
      ...ProcessConfig,
      ...JSON.parse($valid_strategies[chosenStrategies[1]])['properties'],
    }
    strategyDefinitions[1] = JSON.parse($valid_strategies[chosenStrategies[1]])['definitions']
  }

  const openModal = () => {
    open(
      Popup,
      { label: 'Do you want to terminate the experiment?', button: ['Yes', 'Continue with training'] },
      {
        closeButton: true,
        closeOnEsc: true,
        closeOnOuterClick: true,
      },
      {
        onClose: async () => {
          if ($terminate_experiment) {
            await terminateExperiment(experiment_id ?? localStorage.getItem(`battle-on-dataset-${id}`))
            localStorage.removeItem(`battle-on-dataset-${id}`)
            router.goto('/app/')
          }
          $terminate_experiment = false
        },
      }
    )
  }

  experiment_id = localStorage.getItem(`battle-on-dataset-${id}`)

  // Running battle
  if (experiment_id) {
    showConfig = false
    starting = false
    checkStatus()
  }

  // Get valid strategies
  getValidStrategies(id)

  // Get persisted experiments
  getFinishedExperiments()

  async function getDatasetFeatures() {
    availableFeatures = await getFeatures(id)
  }

  async function start() {
    showConfig = false
    starting = true

    // TODO: Features?

    const al_models = [processConfigs[0]['AL_MODEL'], processConfigs[1]['AL_MODEL']]
    const queryConfigs = processConfigs
    delete queryConfigs[0]['AL_MODEL']
    delete queryConfigs[1]['AL_MODEL']

    sendConfig = {
      ...generalConfig,
      exp_configs: [
        {
          AL_MODEL: al_models[0],
          QUERY_STRATEGY: chosenStrategies[0],
          QUERY_STRATEGY_CONFIG: queryConfigs[0],
        },
        {
          AL_MODEL: al_models[1],
          QUERY_STRATEGY: chosenStrategies[1],
          QUERY_STRATEGY_CONFIG: queryConfigs[1],
        },
      ],
      PLOT_CONFIG: {
        FEATURES: Array.isArray(featureConfig) ? featureConfig.map((feature) => feature.value) : undefined,
        CLASSIFICATION_BOUNDARIES: classBoundConfig,
      },
    }

    // For backend pydantic stuff
    sendConfig.exp_configs[0].QUERY_STRATEGY_CONFIG['query_type'] = sendConfig.exp_configs[0].QUERY_STRATEGY
    sendConfig.exp_configs[1].QUERY_STRATEGY_CONFIG['query_type'] = sendConfig.exp_configs[1].QUERY_STRATEGY

    console.debug('Start battle with config:', sendConfig)
    experiment_id = await startBattle(id, sendConfig)

    if (typeof experiment_id === 'number') {
      starting = false
      checkStatus()
    } else {
      notifier.danger('Something went wrong in the backend.', 6000)
      router.goto('/app/')
    }
  }

  async function checkStatus() {
    training = true
    interval = setInterval(async () => {
      if ($isFinished === true) {
        clearInterval(interval)
        await getData()
      } else {
        await getStatus(id, experiment_id)
        if (typeof $isFinished === 'number') {
          remainingTime = formatTime($isFinished)
        } else {
          remainingTime = undefined
        }
      }
    }, 3000)
  }

  async function getData() {
    try {
      await Promise.all([getMetrics(experiment_id), getDiagrams(experiment_id)])
      training = false
    } catch (e) {
      console.warn('Error while loading data:', e)
    }
  }

  async function receiveMetrics() {
    await getMetrics(id)
  }

  function formatTime(duration) {
    // Hours, minutes and seconds
    var hrs = ~~(duration / 3600)
    var mins = ~~((duration % 3600) / 60)
    var secs = ~~duration % 60

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = ''

    if (hrs > 0) {
      ret += '' + hrs + ':' + (mins < 10 ? '0' : '')
    }

    ret += '' + mins + ':' + (secs < 10 ? '0' : '')
    ret += '' + secs
    return ret
  }

  function beforeunload(event: BeforeUnloadEvent) {
    event.preventDefault()
    return (event.returnValue = '')
  }

  function handleFeatureSelect(e) {
    if (featureConfig && featureConfig.length > 2) {
      featureConfig.pop()
      notifier.danger('Only two features allowed here.', 3000)
    }
  }

  onDestroy(() => {
    clearInterval(interval)
  })
</script>

{#if accordingFinishedBattles && accordingFinishedBattles.length > 0 && !experiment_id && showPersisted}
  <div style="display: flex; justify-content: space-between; align-items: center">
    <h1>Persisted Experiments</h1>
    <Button style="height: 50%" on:click={() => (showPersisted = false)}>Start new battle</Button>
  </div>
  <h3>There are some battles persisted for this dataset. Do you want to review one of them?</h3>
  <Persisted
    dataset_id={id}
    on:battleLoaded={async (e) => {
      experiment_id = e.detail['experiment_id']
      sendConfig = e.detail['config']
      showConfig = false
      training = true
      await getData()
    }}
  />
{:else}
  <div style="display: flex; justify-content: space-between; align-items: center">
    <h1>Battle Mode</h1>
    {#if typeof experiment_id === 'number' && $diagrams && $metricData}
      <Button
        style="height: 50%"
        icon="save"
        on:click={async () => {
          const res = await saveExperiment(experiment_id)
          if (res === null) notifier.success('The battle was saved!', 3000)
        }}>Save Battle</Button
      >
    {/if}
  </div>
  <div class="wrapper">
    {#if showConfig}
      <h2><b>General</b> Config</h2>
      <Config alWar strategySchema={GeneralConfig} bind:config={generalConfig} noTitle={true} />
      {#if availableFeatures && availableFeatures.length > 1}
        <h2><b>Plot</b></h2>
        <div class="multi-select">
          <span>Features</span>
          <SvelteSelect
            bind:value={featureConfig}
            items={availableFeatures}
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
      {#if ready}
        <Button label="Submit" icon="checkmark-circle-sharp" on:click={start} />
      {/if}
    {:else if starting}
      <div class="starting">
        <Moon size="30" color="#002557" unit="px" duration="1s" />
        Starting ...
      </div>
    {:else if training}
      <div class="progress-bar">
        <div bind:this={progressElement} class="progress" />
      </div>
      <div style="display: flex; justify-content: space-between;">
        <span style="font-size: 20px"> Get yourself a cup of &#9749; while ALipy is training... </span>
        <Button
          icon="close-outline"
          on:click={() => {
            openModal()
          }}
        />
      </div>
      {#if remainingTime}
        <span style="font-size: 20px"> Remaining time: ca. {remainingTime}</span>
      {/if}
    {:else if dataset}
      <Result dataset_name={dataset['name']} config={sendConfig} />
    {/if}
  </div>
{/if}
<svelte:window on:beforeunload={beforeunload} />

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
