<script lang="ts">
  import { onDestroy, onMount } from 'svelte'
  import embed from 'vega-embed'
  import { diagrams, metricData } from '../../../store/al-war'
  import Table from '../components/labeling/Table.svelte'
  import Image from '../components/labeling/Image.svelte'
  import { getSpecificSample } from '../../../store/samples'
  import { Moon } from 'svelte-loading-spinners'
  import Slider from '@smui/slider'
  import Card from '../../../ui/Card.svelte'

  export let algorithmNames = ['Uncertainty (LC)', 'Random']
  export let dataset_name = 'Unknown dataset'
  export let dataset_id
  export let batch_size = 5

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
    if (sliderValue !== currentIteration) {
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
      const allViews = Object.keys(vega_views)
      delete allViews['acc']
      delete allViews['dmap_1']
      delete allViews['dmap_2']
      await destroyViews(allViews)
      // await destroyViews(['conf_1', 'conf_2'])

      // Push new confidence diagrams
      await pushDiagrams(true)
    }
  }

  async function pushDiagrams(update?: boolean) {
    const vega_options = {
      height: 150,
      tooltip: { theme: 'dark' },
      actions: false,
    }
    const conf_1 = JSON.parse($diagrams['conf'][0][currentIteration - 1])
    const conf_2 = JSON.parse($diagrams['conf'][1][currentIteration - 1])
    const dmap_1 = JSON.parse($diagrams['data_maps'][0])
    const dmap_2 = JSON.parse($diagrams['data_maps'][1])

    vega_views['conf_1'] = await embed(dia_elements_one[0], conf_1, vega_options)
    vega_views['conf_2'] = await embed(dia_elements_two[0], conf_2, vega_options)

    /**
     * TODO: Embed actual diagrams and not the same for every slot
     */

    vega_views['mock_2'] = await embed(dia_elements_one[1], conf_2, vega_options)
    vega_views['mock_4'] = await embed(dia_elements_two[1], conf_1, vega_options)

    // vega_views['mock_3'] = await embed(dia_elements_one[3], conf_1, vega_options)
    // vega_views['mock_5'] = await embed(dia_elements_two[3], conf_2, vega_options)

    if (!update) {
      const acc = JSON.parse($diagrams['acc'])
      vega_views['acc'] = await embed(acc_element, acc, { height: 140 })
      vega_views['dmap_1'] = await embed(dia_elements_one[2], dmap_1, { ...vega_options, actions: true })
      vega_views['dmap_2'] = await embed(dia_elements_two[2], dmap_2, { ...vega_options, actions: true })
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
    if (!$diagrams && localStorage.getItem(`battle-${dataset_id}-diagrams`)) {
      $diagrams = JSON.parse(localStorage.getItem(`battle-${dataset_id}-diagrams`))
      $metricData = JSON.parse(localStorage.getItem(`battle-${dataset_id}-metrics`))
    }

    getSamples()
    await pushDiagrams()
  })

  onDestroy(() => {
    destroyViews()
  })
</script>

<div class="wrapper">
  <Card>
    <div class="left">
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
  </Card>
  <Card>
    <div class="right">
      <div class="battle">
        <div class="process">
          <div class="sample">
            {#if sample_1 && Object.keys(mappings).includes(sample_1.type)}
              <div class="data">
                <svelte:component this={mappings[sample_1.type]} data={sample_1.content} />
              </div>
              <span>Sample ID: {sample_1.id}</span>
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
            <div class="diagram datamap" bind:this={dia_elements_one[2]} />
            <!--
            <div class="diagram" bind:this={dia_elements_one[3]} />
            -->
          </div>
        </div>
        <div class="process">
          <div class="sample">
            {#if sample_2 && Object.keys(mappings).includes(sample_2.type)}
              <div class="data">
                <svelte:component this={mappings[sample_2.type]} data={sample_2.content} />
              </div>
              <span>Sample ID: {sample_2.id}</span>
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
            <div class="diagram datamap" bind:this={dia_elements_two[2]} />
            <!--
            <div class="diagram" bind:this={dia_elements_two[3]} />
            -->
          </div>
        </div>
      </div>
      <hr />
      <div class="accuracy">
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
          {/if}
        </div>
      </div>
    </div>
  </Card>
</div>

<style>
  .wrapper {
    display: grid;
    grid-template-columns: 1fr 5fr;
    column-gap: 15px;
  }

  .left,
  .right {
    display: flex;
    flex-direction: column;
  }

  .left {
    height: 100%;
    justify-content: space-between;
  }

  .dataset-info,
  .metrics,
  .info,
  .process {
    border: 1px solid lightgray;
    border-radius: 5px;
    display: grid;
    grid-template-rows: 250px 4em 1fr;
  }

  h4 {
    margin: 5px;
  }

  p {
    margin: 5px;
  }

  .dataset-info {
    display: grid;
    grid-template-rows: 1fr 1fr 1fr;
    row-gap: 5px;
  }

  .battle {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 50px;
  }

  .sample {
    padding: 2em 2em 0 2em;
    display: flex;
    flex-direction: column;
    row-gap: 1em;
    justify-content: space-between;
  }

  .data {
    overflow: auto;
  }

  .vs {
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    padding: 0 10px;
  }

  .accuracy {
    display: flex;
    flex-direction: column;
  }

  .iterations {
    width: 100%;
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

  .dataset-info > div {
    border-bottom: 1px solid lightgray;
    text-align: center;
  }

  .dataset-info > div:last-child {
    border-bottom: none;
  }

  .diagrams {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    column-gap: 15px;
    row-gap: 15px;
    margin-bottom: 2em;
  }

  .diagram {
    display: flex;
    justify-content: center;
  }

  .datamap {
    grid-column: span 2;
  }

  .diagram:nth-child(even) {
    margin: 0 2em 0 0.5em;
  }

  .diagram:nth-child(odd) {
    margin: 0 0.5em 0 2em;
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
