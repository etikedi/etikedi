<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { getContext, onDestroy } from 'svelte'
  import { Moon } from 'svelte-loading-spinners'
  import { router } from 'tinro'
  import { ProcessConfig } from '../../../../lib/config'
  import { formatTime } from '../../../../lib/human'
  import {
    currentlyViewing,
    diagrams,
    getDiagrams,
    getMetrics,
    getStatus,
    getValidStrategies,
    metricData,
    startBattle,
    terminateExperiment,
    terminate_experiment,
    valid_strategies,
  } from '../../../../store/al-war'
  import { data as datasets, load } from '../../../../store/datasets'
  import Button from '../../../../ui/Button.svelte'
  import BattleConfig from '../../components/battle/Config.svelte'
  import Popup from '../../components/Modal.svelte'

  let showConfig = true,
    ready,
    dataset,
    training = false,
    remainingTime,
    interval,
    loading = false,
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
    battle_id = undefined,
    sendConfig,
    accordingFinishedBattles = []

  /**
   * DEV
   */
  $: if ($metricData) console.debug('metrics:', $metricData)
  $: if ($diagrams) console.debug('diagrams:', $diagrams)

  $: dataset = $datasets[id]
  $: ready = dataset && chosenStrategies[0] && chosenStrategies[1]

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
            await terminateExperiment(id, battle_id)
            router.goto('/app/')
          }
          $terminate_experiment = false
        },
      }
    )
  }

  // Get valid strategies
  getValidStrategies(id)

  async function start() {
    showConfig = false
    loading = true

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
    battle_id = await startBattle(id, sendConfig)

    if (typeof battle_id === 'number') {
      loading = false
      checkStatus()
    } else {
      notifier.danger('Something went wrong in the backend.', 6000)
      router.goto('/app/')
    }
  }

  async function checkStatus() {
    training = true
    interval = setInterval(async () => {
      const status = await getStatus(id, battle_id)
      if (status === null) {
        remainingTime = undefined
      } else if (typeof status === 'number') {
        remainingTime = status.toFixed(2)
      } else if (status === true) {
        clearInterval(interval)
        await getData()
      } else if (typeof status === 'string') {
        notifier.danger(status)
      }
    }, 3000)
  }

  async function getData() {
    try {
      loading = true
      await Promise.all([getMetrics(battle_id), getDiagrams(battle_id)])
      $currentlyViewing['dataset_name'] = dataset.name
      $currentlyViewing['config'] = sendConfig
      $currentlyViewing['battle_id'] = battle_id
      loading = false
      router.goto(`./result`)
    } catch (e) {
      notifier.danger(e)
    }
  }

  async function receiveMetrics() {
    await getMetrics(id)
  }

  onDestroy(() => {
    clearInterval(interval)
  })
</script>

<div class="wrapper">
  {#if showConfig}
    <BattleConfig
      {id}
      bind:classBoundConfig
      bind:generalConfig
      bind:chosenStrategies
      bind:strategySchemas
      bind:strategyDefinitions
      bind:processConfigs
      bind:featureConfig
      on:submit={start}
    />
  {:else if loading}
    <div class="starting">
      Loading ...
      <Moon size="30" color="#002557" unit="px" duration="1s" />
    </div>
  {:else if training}
    <div class="progress-bar">
      <div bind:this={progressElement} class="progress" />
    </div>
    <div style="display: flex; justify-content: space-between;">
      <div class="starting">
        <span style="font-size: 20px"> Get yourself a cup of &#9749; while ALipy is training... </span>
        <Moon size="30" color="#002557" unit="px" duration="1s" />
      </div>
      <Button
        icon="close-outline"
        on:click={() => {
          openModal()
        }}
      />
    </div>
    {#if remainingTime}
      <span style="font-size: 20px"> Remaining time: ca. {remainingTime} min</span>
    {/if}
  {/if}
</div>

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
