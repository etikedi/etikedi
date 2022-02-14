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
  } from '../../../store/al-war'
  import { Moon } from 'svelte-loading-spinners'
  import { notifier } from '@beyonk/svelte-notifications'
  import AlWarComponent from '../components/ALWarComponent.svelte'
  import Card from '../../../ui/Card.svelte'

  let showCache = false,
    showConfig = true,
    ready,
    dataset,
    training = false,
    remainingTime,
    interval,
    starting = false,
    progressElement

  /**
   * DEV
   */
  $: if ($metricData) console.debug($metricData)
  $: if ($diagrams) console.debug($diagrams)

  const { id } = router.params()

  $: dataset = $datasets[id]
  $: ready = dataset && config1 && config2

  if (localStorage.getItem(`battle-${id}-diagrams`) && localStorage.getItem(`battle-${id}-metrics`)) showCache = true
  if (localStorage.getItem(`running-battle-${id}`)) {
    showCache = false
    showConfig = false
    starting = false
    checkStatus()
  }

  let config1 = {
    QUERY_STRATEGY: 'QueryInstanceRandom',
    AL_MODEL: 'RandomForestClassifier',
    STOPPING_CRITERIA_VALUE: 10,
    STOPPING_CRITERIA: 'all_labeled',
    BATCH_SIZE: 5,
  }

  let strategyConfig1 = {
    beta: 1000,
    cls_est: 50,
    disagreement: 'vote_entropy',
    gamma: 0.1,
    lambda_init: 0.1,
    lambda_pace: 0.01,
    measure: 'least_confident',
    method: 'query_by_bagging',
    metric: 'manhattan',
    mode: 'LAL_iterative',
    mu: 0.1,
    rho: 0.1,
    train_slt: true,
  }

  let config2 = { ...config1 }
  let strategyConfig2 = { ...strategyConfig1 }

  async function start() {
    const sendConf1 = {
      ...config1,
      QUERY_STRATEGY_CONFIG: { ...strategyConfig1 },
    }
    const sendConf2 = {
      ...config2,
      QUERY_STRATEGY_CONFIG: { ...strategyConfig2 },
    }
    console.debug('Config 1', sendConf1, 'Config 2', sendConf2)
    showConfig = false
    starting = true
    const started = await startBattle(id, sendConf1, sendConf2)
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

  onDestroy(() => {
    clearInterval(interval)
  })
</script>

{#if showCache}
  <Card>
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
  </Card>
{:else}
  <div class="wrapper">
    {#if showConfig}
      <div class="config-wrapper">
        <Config bind:config={config1} bind:strategyConfig={strategyConfig1} alWar />
        <Config bind:config={config2} bind:strategyConfig={strategyConfig2} alWar />
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
