<script>
  import Button from '../../../ui/Button.svelte'
  import Input from '../../../ui/Input.svelte'
  import Config from './Config.svelte'
  import { data as datasets } from '../../../store/datasets'
  import { router } from 'tinro'

  let showConfig = true,
    config1,
    config2,
    ready,
    dataset,
    training = false,
    progressElement

  const { id } = router.params()

  $: dataset = $datasets[id]
  $: ready = dataset && config1 && config2

  async function submit() {
    console.debug('Config 1', config1, 'Config 2', config2)
    showConfig = false
    training = true
    setTimeout(() => (training = false), 10000)
  }
</script>

<div class="wrapper">
  {#if showConfig}
    <div class="config-wrapper">
      <Config bind:config={config1} alWar />
      <Config bind:config={config2} alWar />
    </div>
    {#if ready}
      <Button label="Submit" icon="checkmark-circle-sharp" on:click={submit} />
    {/if}
  {:else if training}
    <div class="progress-bar">
      <div bind:this={progressElement} class="progress" />
    </div>
    <span style="font-size: 20px"> Get yourself a cup of &#9749; while ALipy is training... </span>
  {:else}
    <div class="al-war-wrapper">mooooin</div>
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
</style>
