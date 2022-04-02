<script lang="ts">
  import Button from '../../../ui/Button.svelte'
  import Config from './Config.svelte'
  import { data as datasets } from '../../../store/datasets'
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
  } from '../../../store/al-war'
  import { Moon } from 'svelte-loading-spinners'
  import { notifier } from '@beyonk/svelte-notifications'
  import AlWarComponent from '../components/ALWarComponent.svelte'
  import Popup from '../components/Modal.svelte'
  import Card from '../../../ui/Card.svelte'
  import Select from '../../../ui/Select.svelte'
  import { GeneralConfig, ProcessConfig } from '../../../lib/config'

  let showCache = false,
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
    processConfigs = [{}, {}],
    strategySchemas = [],
    strategyDefinitions = [],
    { open } = getContext('simple-modal'),
    { close } = getContext('simple-modal'),
    { id } = router.params(),
    experiment_id = undefined,
    sendConfig

  /**
   * DEV
   */
  $: if ($metricData) console.debug($metricData)
  $: if ($diagrams) console.debug($diagrams)
  $: if (processConfigs) console.debug('processConfigs', processConfigs)

  $: dataset = $datasets[id]
  $: ready = dataset && chosenStrategies[0] && chosenStrategies[1]

  $: if (chosenStrategies[0]) {
    console.debug($valid_strategies)
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
        onClose: () => {
          if ($terminate_experiment) {
            localStorage.removeItem(`battle-on-dataset-${id}`)
            router.goto('/app/')
            /** TODO: Terminate experiment backend call */
          }
          $terminate_experiment = false
        },
      }
    )
    console.debug(open)
  }

  experiment_id = localStorage.getItem(`battle-on-dataset-${id}`)

  // Running battle
  if (experiment_id) {
    showCache = false
    showConfig = false
    starting = false
    checkStatus()
  }

  // Get valid strategies
  getValidStrategies(id)

  async function start() {
    showConfig = false
    starting = true

    // TODO: Features?

    const al_models = [processConfigs[0]['AL_MODEL'], processConfigs[0]['AL_MODEL']]
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
        getData(experiment_id)
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

  async function getData(experiment_id) {
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

  /*
  window.onpopstate = function (e) {
    if (confirm('Do you want to terminate the training?')) {
      console.debug("terminate")
    }
    return e
  }
  */

  onDestroy(() => {
    clearInterval(interval)
  })
</script>

{#if showCache}
  <Card>
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
      <span>We saved your last simulation with this dataset. Do you want to view it again?</span>
      <div style="display: grid; grid-template-columns: 200px 200px; column-gap: 15px; margin-top: 15px">
        <Button
          on:click={() => {
            showConfig = false
            showCache = false
          }}>Yes</Button
        >
        <Button on:click={() => (showCache = false)}>Start new battle</Button>
      </div>
    </div>
  </Card>
{:else}
  <div class="wrapper">
    {#if showConfig}
      <Config alWar strategySchema={GeneralConfig} bind:config={generalConfig} name="General" />
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
                <Config
                  bind:config={processConfigs[0]}
                  strategySchema={strategySchemas[0]}
                  strategyDefinitions={strategyDefinitions[0]}
                  alWar
                  name="Strategy"
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
                <Config
                  bind:config={processConfigs[1]}
                  strategySchema={strategySchemas[1]}
                  strategyDefinitions={strategyDefinitions[1]}
                  alWar
                  name="Strategy"
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
      <AlWarComponent dataset_name={dataset['name']} config={sendConfig} />
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
</style>
