<script lang="ts">
  import Button from '../../../ui/Button.svelte'
  import Config from './Config.svelte'
  import { data as datasets } from '../../../store/datasets'
  import { router } from 'tinro'
  import { onDestroy, onMount } from 'svelte'
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
  } from '../../../store/al-war'
  import { Moon } from 'svelte-loading-spinners'
  import { notifier } from '@beyonk/svelte-notifications'
  import AlWarComponent from '../components/ALWarComponent.svelte'
  import Card from '../../../ui/Card.svelte'
  import Select from '../../../ui/Select.svelte'
  import { mockSendConfig } from '../../../lib/al_configs'
  import { ProcessConfig } from '../../../store/config'

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
    processConfigs = [{}, {}],
    strategySchemas = [],
    strategyDefinitions = []

  /**
   * DEV
   */
  $: if ($metricData) console.debug($metricData)
  $: if ($diagrams) console.debug($diagrams)
  $: if (processConfigs) console.debug('processConfigs', processConfigs)
  $: if (chosenStrategies) console.debug('chosenStrategies', chosenStrategies)
  $: if (strategySchemas) console.debug('strategySchemas', strategySchemas)

  const { id } = router.params()

  $: dataset = $datasets[id]
  $: ready = dataset && chosenStrategies[0] && chosenStrategies[1]

  $: if (chosenStrategies[0]) {
    strategySchemas[0] = null
    setTimeout(() => {
      strategySchemas[0] = {
        ...ProcessConfig,
        ...JSON.parse($valid_strategies[chosenStrategies[0]])['properties'],
      }
    }, 300)
    strategyDefinitions[0] = JSON.parse($valid_strategies[chosenStrategies[0]])['definitions']
  }

  $: if (chosenStrategies[1]) {
    strategySchemas[1] = null
    setTimeout(() => {
      strategySchemas[1] = {
        ...ProcessConfig,
        ...JSON.parse($valid_strategies[chosenStrategies[1]])['properties'],
      }
    }, 300)
    strategyDefinitions[1] = JSON.parse($valid_strategies[chosenStrategies[1]])['definitions']
  }

  // Existing cache
  if (localStorage.getItem(`battle-${id}-diagrams`) && localStorage.getItem(`battle-${id}-metrics`)) showCache = true

  // Running battle
  if (localStorage.getItem(`running-battle-${id}`)) {
    showCache = false
    showConfig = false
    starting = false
    checkStatus()
  }

  // Get valid strategies
  getValidStrategies(id)

  async function start() {
    console.debug('Mock Send:', mockSendConfig)
    localStorage.setItem(`battle-${id}-config1`, JSON.stringify(mockSendConfig))
    localStorage.setItem(`battle-${id}-config2`, JSON.stringify(mockSendConfig))
    showConfig = false
    starting = true
    const started = await startBattle(id, mockSendConfig)
    if (started === null) {
      starting = false
      checkStatus()
    } else {
      notifier.danger('Something went wrong in the backend.', 6000)
      router.goto('/app/')
    }
  }

  async function checkStatus() {
    training = true
    localStorage.setItem(`running-battle-${id}`, 'true')
    interval = setInterval(async () => {
      if ($isFinished === true) {
        clearInterval(interval)
        localStorage.removeItem(`running-battle-${id}`)
        getData()
      } else {
        await getStatus(id)
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
      await Promise.all([getMetrics(id), getDiagrams(id)])
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
      <div class="config-wrapper">
        {#if $valid_strategies}
          <div>
            <Select
              bind:value={chosenStrategies[0]}
              values={Object.keys($valid_strategies)}
              emptyFirst
              label="Query strategy"
            />
            {#if chosenStrategies[0] && strategySchemas[0]}
              <Config
                bind:config={processConfigs[0]}
                strategySchema={strategySchemas[0]}
                strategyDefinitions={strategyDefinitions[0]}
                alWar
              />
            {/if}
          </div>
          <div>
            <Select
              bind:value={chosenStrategies[1]}
              values={Object.keys($valid_strategies)}
              emptyFirst
              label="Query strategy"
            />
            {#if chosenStrategies[1] && strategySchemas[1]}
              <Config
                bind:config={processConfigs[1]}
                strategySchema={strategySchemas[1]}
                strategyDefinitions={strategyDefinitions[1]}
                alWar
              />
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
      <span style="font-size: 20px"> Get yourself a cup of &#9749; while ALipy is training... </span>
      {#if remainingTime}
        <span style="font-size: 20px"> Remaining time: ca. {remainingTime}</span>
      {/if}
    {:else if dataset}
      <AlWarComponent dataset_name={dataset['name']} dataset_id={id} />
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
