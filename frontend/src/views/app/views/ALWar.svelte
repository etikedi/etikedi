<script>
  import Button from '../../../ui/Button.svelte'
  import Input from '../../../ui/Input.svelte'
  import Config from './Config.svelte'
  import { data as datasets } from '../../../store/datasets'
  import { router } from 'tinro'

  let showConfig = false,
    config1,
    config2,
    ready,
    dataset,
    training = false,
    progressElement

  const { id } = router.params()

  const algorithmNames = ["Uncertainty (LC)", "Random"]
  const metrics = {
    "Acc (test)": ["61%", "58%"], 
    "Mean Annotation Cost": ["61%", "58%"], 
    "F1-AUC (test)": ["61%", "58%"], 
    "Average distance labeled (test)": ["61%", "58%"], 
    "Average distance unlabeled (test)": ["61%", "58%"], 
    "Total Computation Time": ["61%", "58%"]
  }

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
    <div class="al-war-wrapper">
      <div class="data section">
        <div class="dataset-info">
          <div>Dataset: DWTC</div>
          <div>AL Cycle: 11/50</div>
          <div>Random Forest Classifier</div>
          <div>Batch Size: 1</div>
        </div>
        <div class="metrics">
          {#if algorithmNames.length === 2 && metrics}
          <table>
            <tr style="height: 100px">
              <th></th>
              <th class="heading">{algorithmNames[0]}</th>
              <th class="heading">{algorithmNames[1]}</th>
            </tr>
            {#each Object.entries(metrics) as metric}
            <tr>
              <td style="font-weight: bold">{metric[0]}</td>
              <td style="text-align: center">{metric[1][0]}</td>
              <td style="text-align: center">{metric[1][1]}</td>
            </tr>
            {/each}
            </table>
          {/if}
        </div>
        <div class="info">
          <div>similar</div>
          <div>percentage</div>
          <div>percentage</div>
        </div>
      </div>
      <div class="first section">
        <div class="sample">sample</div>
        <hr />
        <div class="diagrams">diagram</div>
      </div>
      <div class="vs section">vs</div>
      <div class="second section">
        <div class="sample">sample</div>
        <hr />
        <div class="diagrams">diagram</div>
      </div>
      <div class="accuracy section">
      </div>
    </div>
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

  .al-war-wrapper {
    display: grid;
    grid-template-columns: 0.65fr 1fr 90px 1fr;
    grid-template-rows: 1fr 1fr 0.8fr;
    gap: 15px;
    grid-template-areas:
      'data first vs second'
      'data first vs second'
      'data accuracy accuracy accuracy';
  }

  .section {
    display: grid;
  }

  .data {
    grid-area: data;
    grid-template-rows: 1fr 3fr 1fr;
    row-gap: 20px;
  }

  .first {
    grid-area: first;
  }

  .second {
    grid-area: second;
  }

  .first,
  .second {
    grid-template-rows: 1fr 40px 1fr;
  }

  .vs {
    grid-area: vs;
  }

  .accuracy {
    grid-area: accuracy;
    align-items: center;
  }

  .heading {
    transform: rotate(-90deg);
    font-weight: normal;
    margin-bottom: 10px;
  }

  .metrics {
    border-top: 1px solid lightgray;
    border-bottom: 1px solid lightgray;
  }

  .al-war-wrapper > div {
    border: 1px solid lightgray;
  }
</style>
