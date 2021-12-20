<script>
  import { getDiagram } from '../../../store/datasets'
  import { router } from 'tinro'
  import { onDestroy, onMount } from 'svelte'
  import embed from 'vega-embed'

  export let algorithmNames = ['Uncertainty (LC)', 'Random']
  export let dataset_info = {
    name: 'DWTC',
    cycle: 11,
    cycle_total: 50,
    classifier: 'Random Forest Classifier',
    batch_size: 1,
  }

  let acc_element,
    dia_elements_one = [],
    dia_elements_two = [],
    vega_views = []

  let spec = {
    $schema: 'https://vega.github.io/schema/vega/v5.json',
    description: 'A basic line chart example.',
    width: 500,
    height: 200,
    padding: 5,

    signals: [
      {
        name: 'interpolate',
        value: 'linear',
        bind: {
          input: 'select',
          options: [
            'basis',
            'cardinal',
            'catmull-rom',
            'linear',
            'monotone',
            'natural',
            'step',
            'step-after',
            'step-before',
          ],
        },
      },
    ],

    data: [
      {
        name: 'table',
        values: [
          { x: 0, y: 28, c: 0 },
          { x: 0, y: 20, c: 1 },
          { x: 1, y: 43, c: 0 },
          { x: 1, y: 35, c: 1 },
          { x: 2, y: 81, c: 0 },
          { x: 2, y: 10, c: 1 },
          { x: 3, y: 19, c: 0 },
          { x: 3, y: 15, c: 1 },
          { x: 4, y: 52, c: 0 },
          { x: 4, y: 48, c: 1 },
          { x: 5, y: 24, c: 0 },
          { x: 5, y: 28, c: 1 },
          { x: 6, y: 87, c: 0 },
          { x: 6, y: 66, c: 1 },
          { x: 7, y: 17, c: 0 },
          { x: 7, y: 27, c: 1 },
          { x: 8, y: 68, c: 0 },
          { x: 8, y: 16, c: 1 },
          { x: 9, y: 49, c: 0 },
          { x: 9, y: 25, c: 1 },
        ],
      },
    ],

    scales: [
      {
        name: 'x',
        type: 'point',
        range: 'width',
        domain: { data: 'table', field: 'x' },
      },
      {
        name: 'y',
        type: 'linear',
        range: 'height',
        nice: true,
        zero: true,
        domain: { data: 'table', field: 'y' },
      },
      {
        name: 'color',
        type: 'ordinal',
        range: 'category',
        domain: { data: 'table', field: 'c' },
      },
    ],

    axes: [
      { orient: 'bottom', scale: 'x' },
      { orient: 'left', scale: 'y' },
    ],

    marks: [
      {
        type: 'group',
        from: {
          facet: {
            name: 'series',
            data: 'table',
            groupby: 'c',
          },
        },
        marks: [
          {
            type: 'line',
            from: { data: 'series' },
            encode: {
              enter: {
                x: { scale: 'x', field: 'x' },
                y: { scale: 'y', field: 'y' },
                stroke: { scale: 'color', field: 'c' },
                strokeWidth: { value: 2 },
              },
              update: {
                interpolate: { signal: 'interpolate' },
                strokeOpacity: { value: 1 },
              },
              hover: {
                strokeOpacity: { value: 0.5 },
              },
            },
          },
        ],
      },
    ],
  }

  const { id } = router.params()

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

  async function getDia() {
    const diagrams = await getDiagram(id)
    const vega_options = {
      width: 75,
      height: 150,
      tooltip: { theme: 'dark' },
      actions: false,
    }
    for (let i = 0; i < 4; i++) {
      vega_views.push(await embed(dia_elements_one[i], JSON.parse(diagrams[i]), vega_options))
      vega_views.push(await embed(dia_elements_two[i], JSON.parse(diagrams[i]), vega_options))
    }
    vega_views.push(await embed(acc_element, spec, { height: 200, width: 800, actions: false }))
  }

  onMount(() => {
    // getDia()
  })

  onDestroy(() => {
    for (const view of vega_views) {
      view.view.finalize()
    }
  })
</script>

<div class="al-war-wrapper">
  <div class="data section">
    <div class="dataset-info">
      <div>
        <h4>Dataset:</h4>
        <p>{dataset_info.name}</p>
      </div>
      <div>
        <h4>AL Cycle:</h4>
        <p>{dataset_info.cycle}/{dataset_info.cycle_total}</p>
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
    <div class="sample">sample</div>
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
    <div class="sample">sample</div>
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
    grid-template-rows: 190px 3fr 280px;
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
    grid-template-rows: 1fr 1fr;
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
