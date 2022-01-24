<script lang="ts">
  import { router } from 'tinro'
  import { onDestroy, onMount } from 'svelte'
  import embed from 'vega-embed'
  import { diagrams, metricData } from '../../../store/al-war'
  import Table from '../components/labeling/Table.svelte'
  import Image from '../components/labeling/Image.svelte'
  import { getSpecificSample } from '../../../store/samples'
  import { Moon } from 'svelte-loading-spinners'
  import Slider from '@smui/slider'
  import { CONTINUOUS_TO_DISCRETE_SCALES } from 'vega-lite/build/src/scale'

  export let algorithmNames = ['Uncertainty (LC)', 'Random']
  export let dataset_name = 'Dataset 1'
  export let batch_size = 1

  let acc_element,
    dia_elements_one = [],
    dia_elements_two = [],
    vega_views = {},
    sliderValue = 1,
    currentIteration = 1,
    sample_1,
    sample_2

  // TODO: From store
  const metrics = {
    Acc: ['61%', '58%'],
    'Mean Annotation Cost': ['6s', '9s'],
    'F1-AUC (test)': ['63%', '60%'],
  }

  const sample_info = {
    '# Similar samples': '32/240',
    'Percentage labeled': '0.51%',
    'Percentage unlabeled': '99.48%',
  }

  const mappings = {
    tables: Table,
    image: Image,
    text: Table,
  }

  async function changeIteration() {
    currentIteration = sliderValue

    // Label percentage
    const labeled = Math.round($metricData['iterations'][currentIteration - 1][0]['percentage_labeled'] * 10000) / 100
    sample_info['Percentage labeled'] = labeled + '%'
    sample_info['Percentage unlabeled'] = Math.round((100 - labeled) * 100) / 100 + '%'

    // Annotation cost
    const cost_1 = Math.round($metricData['iterations'][currentIteration - 1][0]['time'] * 100) / 100
    const cost_2 = Math.round($metricData['iterations'][currentIteration - 1][1]['time'] * 100) / 100
    metrics['Mean Annotation Cost'] = [cost_1 + 's', cost_2 + 's']

    // Fetch sample (hopefully in background)
    getSamples()

    // Destroy confidence diagrams
    await destroyViews(['conf_1', 'conf_2'])

    // Push new confidence diagrams
    await pushDiagrams(true)
  }

  async function pushDiagrams(update?: boolean) {
    const vega_options = {
      width: 75,
      height: 150,
      tooltip: { theme: 'dark' },
      actions: false,
    }
    const conf_1 = JSON.parse($diagrams['conf'][0][currentIteration - 1])
    const conf_2 = JSON.parse($diagrams['conf'][1][currentIteration - 1])

    vega_views['conf_1'] = await embed(dia_elements_one[0], conf_1, vega_options)
    vega_views['conf_2'] = await embed(dia_elements_two[0], conf_2, vega_options)

    if (!update) {
      const acc = JSON.parse($diagrams['acc'])
      vega_views['acc'] = await embed(acc_element, acc, { height: 110, width: 800, actions: false })
    }
  }

  function destroyViews(viewList?) {
    if (viewList) {
      for (const view of viewList) {
        vega_views[view].view.finalize()
      }
    } else {
      for (const view of Object.keys(vega_views)) {
        vega_views[view].view.finalize()
      }
    }
  }

  async function getSamples() {
    const id_1 = $metricData['iterations'][currentIteration - 1][0]['sample_ids'][0]
    const id_2 = $metricData['iterations'][currentIteration - 1][1]['sample_ids'][0]

    sample_1 = await getSpecificSample(id_1)
    sample_2 = await getSpecificSample(id_2)
  }

  onMount(async () => {
    /**
     * DEV
     */
    if (localStorage.getItem('diagrams')) {
      $diagrams = JSON.parse(localStorage.getItem('diagrams'))
      $metricData = JSON.parse(localStorage.getItem('metrics'))
    }

    getSamples()
    await pushDiagrams()
  })

  onDestroy(() => {
    destroyViews()
  })
</script>

<div class="al-war-wrapper">
  <div class="data section">
    <div class="dataset-info">
      <div>
        <h4>Dataset:</h4>
        <p>{dataset_name}</p>
      </div>
      <div>
        <h4>AL Cycle:</h4>
        {#if $metricData && $metricData['iterations']}
          <p>{currentIteration}/{$metricData['iterations'].length}</p>
        {/if}
      </div>
      <div>
        <h4>Batch size:</h4>
        <p>{batch_size}</p>
      </div>
    </div>
    <div class="metrics">
      {#if algorithmNames.length === 2 && metrics}
        <table>
          <tr style="height: 100px">
            <th />
            <th class="heading">{algorithmNames[0]}</th>
            <th class="heading">{algorithmNames[1]}</th>
          </tr>
          {#each Object.entries(metrics) as metric}
            <tr>
              <td style="font-weight: bold; text-align: end;">{metric[0]}</td>
              <td style="text-align: center">{metric[1][0]}</td>
              <td style="text-align: center">{metric[1][1]}</td>
            </tr>
          {/each}
        </table>
      {/if}
    </div>
    <div class="info">
      {#each Object.entries(sample_info) as info}
        <div class="row">
          <span style="font-weight: bold">{info[0]}</span>
          <span>{info[1]}</span>
        </div>
      {/each}
    </div>
  </div>
  <div class="first section">
    <div class="sample">
      {#if sample_1 && Object.keys(mappings).includes(sample_1.type)}
        <svelte:component this={mappings[sample_1.type]} data={sample_1.content} />
      {:else if sample_1}
        <p>Unsupported type {sample_1.type}</p>
      {:else}
        <Moon size="30" color="#002557" unit="px" duration="1s" />
      {/if}
    </div>
    <hr />
    <div class="diagrams">
      <div class="diagram" bind:this={dia_elements_one[0]} />
      <div class="diagram" bind:this={dia_elements_one[1]} />
      <div class="diagram" bind:this={dia_elements_one[2]} />
      <div class="diagram" bind:this={dia_elements_one[3]} />
    </div>
  </div>
  <div class="vs section">
    <img src="/img/vs.png" alt="vs Icon" />
  </div>
  <div class="second section">
    <div class="sample">
      {#if sample_2 && Object.keys(mappings).includes(sample_2.type)}
        <svelte:component this={mappings[sample_2.type]} data={sample_2.content} />
      {:else if sample_2}
        <p>Unsupported type {sample_2.type}</p>
      {:else}
        <Moon size="30" color="#002557" unit="px" duration="1s" />
      {/if}
    </div>
    <hr />
    <div class="diagrams">
      <div class="diagram" bind:this={dia_elements_two[0]} />
      <div class="diagram" bind:this={dia_elements_two[1]} />
      <div class="diagram" bind:this={dia_elements_two[2]} />
      <div class="diagram" bind:this={dia_elements_two[3]} />
    </div>
  </div>
  <div class="accuracy section">
    <div bind:this={acc_element} />
    <div class="iterations">
      {#if $metricData && $metricData['iterations']}
        <Slider
          bind:value={sliderValue}
          on:click={changeIteration}
          min={1}
          max={$metricData['iterations'].length}
          discrete
          tickMarks
          input$aria-label="Tick slider"
        />
        <!--
        <input
          type="range"
          bind:this={slider}
          bind:value={sliderValue}
          min="1"
          max={$metricData['iterations'].length}
          list="tickmarks"
        />
        <datalist id="tickmarks">
          {#each $metricData['iterations'] as _, i}
            <option value={i + 1} label={i + 1} />
          {/each}
        </datalist>
      -->
      {/if}
    </div>
  </div>
</div>

<style>
  h4 {
    margin: 5px;
  }

  p {
    margin: 5px;
  }

  .al-war-wrapper {
    display: grid;
    grid-template-columns: 0.65fr 1fr 90px 1fr;
    grid-template-rows: 200px 387px 235px;
    row-gap: 15px;
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
    margin-right: 15px;
  }

  .dataset-info {
    display: grid;
    grid-template-rows: 1fr 1fr 1fr;
    row-gap: 5px;
  }

  .first {
    grid-area: first;
  }

  .second {
    grid-area: second;
  }

  .first,
  .second {
    grid-template-rows: 1fr 40px 2fr;
  }

  .sample {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .vs {
    grid-area: vs;
    align-items: center;
    justify-content: center;
    border: none;
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
    border: 1px solid lightgray;
  }

  .info {
    border: 1px solid lightgray;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .row {
    display: grid;
    grid-template-columns: 1fr 90px;
    column-gap: 10px;
    text-align: end;
    margin-right: 15px;
  }

  .al-war-wrapper > div {
    border: 1px solid lightgray;
  }

  .al-war-wrapper > .vs {
    border: none;
  }

  .dataset-info > div {
    border: 1px solid lightgray;
    text-align: center;
  }

  .diagrams {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    column-gap: 15px;
    row-gap: 15px;
  }

  .diagram {
    border: 1px solid lightgray;
  }

  table {
    border-collapse: collapse;
  }

  tr {
    border-bottom: 1px solid lightgray;
  }

  tr:last-child {
    border-bottom: none;
  }
</style>
