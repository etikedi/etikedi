<script lang="ts">
  import { onDestroy, onMount } from 'svelte'
  import embed from 'vega-embed'
  import { vega } from 'vega-embed'
  import { diagrams, metricData } from '../../../store/al-war'
  import Table from '../components/labeling/Table.svelte'
  import Image from '../components/labeling/Image.svelte'
  import { getSpecificSample } from '../../../store/samples'
  import { Moon } from 'svelte-loading-spinners'
  import Slider from '@smui/slider'
  import Card from '../../../ui/Card.svelte'
  import Input from '../../../ui/Input.svelte'
  import Button from '../../../ui/Button.svelte'

  export let dataset_name = 'Unknown dataset'
  export let config

  let acc_element,
    dia_elements_one = [],
    dia_elements_two = [],
    vega_views = {},
    sliderValue = 1,
    inputValue = 1,
    currentIteration = 1,
    stepSize = 1,
    sample_1,
    sample_2,
    sliderDiv,
    sampleIndexes = { process1: 0, process2: 0 },
    metrics = []

  // TODO: From store
  $: if ($metricData) {
    metrics = $metricData['iterations'][currentIteration - 1].map((process) => {
      return {
        ...process['metrics'],
      }
    })
  }

  const sample_info = {
    'Similar samples': '0%',
    'Percentage labeled': '0.51%',
    'Percentage unlabeled': '99.48%',
  }

  const mappings = {
    tables: Table,
    image: Image,
    text: Table,
  }

  $: if ($metricData && $metricData['iterations'] && currentIteration) changeIteration()

  async function changeIteration() {
    // Sync values
    sliderValue = parseInt(currentIteration, 10)
    inputValue = parseInt(currentIteration, 10)

    // Label percentage
    const labeled =
      Math.round($metricData['iterations'][currentIteration - 1][0]['meta']['percentage_labeled'] * 10000) / 100
    sample_info['Similar samples'] = ($metricData['percentage_similar'][currentIteration - 1] * 100).toFixed(1) + '%'
    sample_info['Percentage labeled'] = labeled + '%'
    sample_info['Percentage unlabeled'] = Math.round((100 - labeled) * 100) / 100 + '%'

    // Annotation cost
    const cost_1 = Math.round($metricData['iterations'][currentIteration - 1][0]['meta']['time'] * 100) / 100
    const cost_2 = Math.round($metricData['iterations'][currentIteration - 1][1]['meta']['time'] * 100) / 100
    metrics[0]['Training Time'] = cost_1 + 's'
    metrics[1]['Training Time'] = cost_2 + 's'

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

  async function pushDiagrams(update?: boolean) {
    const logLevel = vega.Error
    const vega_options = {
      height: 150,
      tooltip: { theme: 'dark' },
      actions: false,
      logLevel,
    }
    const conf_1 = JSON.parse($diagrams['conf'][0][currentIteration - 1])
    const conf_2 = JSON.parse($diagrams['conf'][1][currentIteration - 1])
    const classBound1 = JSON.parse($diagrams['classification_boundaries'][0][currentIteration - 1])
    const classBound2 = JSON.parse($diagrams['classification_boundaries'][1][currentIteration - 1])
    const vector1 = JSON.parse($diagrams['vector_space'][0][currentIteration - 1])
    const vector2 = JSON.parse($diagrams['vector_space'][1][currentIteration - 1])
    const dmap_1 = JSON.parse($diagrams['data_maps'][0][currentIteration - 1])
    const dmap_2 = JSON.parse($diagrams['data_maps'][1][currentIteration - 1])

    vega_views['conf_1'] = await embed(dia_elements_one[0], conf_1, vega_options)
    vega_views['conf_2'] = await embed(dia_elements_two[0], conf_2, vega_options)

    vega_views['classBound1'] = await embed(dia_elements_one[1], classBound1, vega_options)
    vega_views['classBound2'] = await embed(dia_elements_two[1], classBound2, vega_options)

    vega_views['vector1'] = await embed(dia_elements_one[2], vector1, { ...vega_options, actions: true })
    vega_views['vector2'] = await embed(dia_elements_two[2], vector2, { ...vega_options, actions: true })

    vega_views['dmap_1'] = await embed(dia_elements_one[3], dmap_1, { ...vega_options, actions: true })
    vega_views['dmap_2'] = await embed(dia_elements_two[3], dmap_2, { ...vega_options, actions: true })

    if (!update) {
      const acc = JSON.parse($diagrams['acc'])
      getStepSize($metricData['iterations'].length)
      vega_views['acc'] = await embed(acc_element, acc, { height: 140, logLevel })
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
    const id_1 = $metricData['iterations'][currentIteration - 1][0]['meta']['sample_ids'][0]
    const id_2 = $metricData['iterations'][currentIteration - 1][1]['meta']['sample_ids'][0]

    sample_1 = await getSpecificSample(id_1)
    sample_2 = await getSpecificSample(id_2)
  }

  async function getSampleFromId(sample_id: number, process: 1 | 2) {
    const sample = await getSpecificSample(sample_id)
    if (process === 1) sample_1 = sample
    else sample_2 = sample
  }

  function getStepSize(length: number) {
    const pxPerStep = sliderDiv.offsetWidth / length
    if (pxPerStep < 15) {
      stepSize++
      getStepSize(Math.round(length / 2))
    } else {
      return stepSize
    }
  }

  onMount(async () => {
    /**
     * DEV
     */
    const loadMock = false
    if (loadMock && !$diagrams && !$metricData) {
      config = {
        BATCH_SIZE: 5,
        exp_configs: [
          {
            QUERY_STRATEGY: 'QueryInstanceUncertainty',
            AL_MODEL: 'DecisionTreeClassifier',
          },
          {
            QUERY_STRATEGY: 'QueryInstanceRandom',
            AL_MODEL: 'MLP',
          },
        ],
      }
      const diag = await fetch('/data/diagrams.json')
      const diagJson = await diag.json()
      $diagrams = diagJson
      const metr = await fetch('/data/metricData.json')
      const metrJson = await metr.json()
      $metricData = metrJson
    }

    getSamples()
    await pushDiagrams()
  })

  onDestroy(() => {
    destroyViews()
  })
</script>

{#if $metricData && $diagrams && config}
  <div class="wrapper">
    <Card>
      <div class="left">
        <div class="dataset-info">
          <div>
            <h4>Dataset:</h4>
            <p>{dataset_name}</p>
          </div>
          {#if $metricData && $metricData['iterations']}
            <div>
              <h4>AL Cycle:</h4>
              <p>{currentIteration}/{$metricData['iterations'].length}</p>
            </div>
          {/if}
          <div>
            <h4>Batch size:</h4>
            <p>{config['BATCH_SIZE']}</p>
          </div>
        </div>
        <div class="metrics">
          <table>
            <tr>
              <th />
              <th>
                <div class="heading">
                  {config['exp_configs'][0]['QUERY_STRATEGY']}
                </div>
              </th>
              <th>
                <div class="heading">
                  {config['exp_configs'][1]['QUERY_STRATEGY']}
                </div>
              </th>
            </tr>

            {#if metrics.length > 1}
              {#each Object.keys(metrics[0]) as key}
                <tr>
                  <td style="font-weight: bold;">{key}</td>
                  <td style="padding: 5px 10px; text-align: center">
                    {typeof metrics[0][key] == 'number' ? metrics[0][key].toFixed(3) : metrics[0][key]}
                  </td>
                  <td style="padding: 5px 10px; text-align: center">
                    {typeof metrics[1][key] == 'number' ? metrics[1][key].toFixed(3) : metrics[1][key]}
                  </td>
                </tr>
              {/each}
            {/if}
          </table>
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
            <div class="process-info">
              <h2>{config['exp_configs'][0]['QUERY_STRATEGY']}</h2>
              <span><b>AL Model: </b>{config['exp_configs'][0]['AL_MODEL']}</span>
            </div>
            <hr />
            <div class="sample">
              <div class="sample-navigation">
                <div>
                  {#if sampleIndexes.process1 > 0}
                    <ion-icon
                      name="arrow-back-circle-outline"
                      on:click={() => {
                        sampleIndexes.process1 = sampleIndexes.process1 - 1
                        getSampleFromId(
                          $metricData['iterations'][currentIteration - 1][0]['meta']['sample_ids'][
                            sampleIndexes.process1
                          ],
                          1
                        )
                      }}
                    />
                  {/if}
                </div>
                <div>
                  {#if sampleIndexes.process1 < $metricData['iterations'][currentIteration - 1][0]['meta']['sample_ids'].length - 1}
                    <ion-icon
                      name="arrow-forward-circle-outline"
                      on:click={() => {
                        sampleIndexes.process1 = sampleIndexes.process1 + 1
                        getSampleFromId(
                          $metricData['iterations'][currentIteration - 1][0]['meta']['sample_ids'][
                            sampleIndexes.process1
                          ],
                          1
                        )
                      }}
                    />
                  {/if}
                </div>
              </div>
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
              <div class="diagram" bind:this={dia_elements_one[2]} />
              <div class="diagram" bind:this={dia_elements_one[3]} />
            </div>
          </div>
          <div class="process">
            <div class="process-info">
              <h2>{config['exp_configs'][1]['QUERY_STRATEGY']}</h2>
              <span><b>AL Model: </b>{config['exp_configs'][1]['AL_MODEL']}</span>
            </div>
            <hr />
            <div class="sample">
              <div class="sample-navigation">
                <div>
                  {#if sampleIndexes.process2 > 0}
                    <ion-icon
                      name="arrow-back-circle-outline"
                      on:click={() => {
                        sampleIndexes.process2 = sampleIndexes.process2 - 1
                        getSampleFromId(
                          $metricData['iterations'][currentIteration - 1][1]['meta']['sample_ids'][
                            sampleIndexes.process2
                          ],
                          2
                        )
                      }}
                    />
                  {/if}
                </div>
                <div>
                  {#if sampleIndexes.process2 < $metricData['iterations'][currentIteration - 1][1]['meta']['sample_ids'].length - 1}
                    <ion-icon
                      name="arrow-forward-circle-outline"
                      on:click={() => {
                        sampleIndexes.process2 = sampleIndexes.process2 + 1
                        getSampleFromId(
                          $metricData['iterations'][currentIteration - 1][1]['meta']['sample_ids'][
                            sampleIndexes.process2
                          ],
                          2
                        )
                      }}
                    />
                  {/if}
                </div>
              </div>
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
              <div class="diagram" bind:this={dia_elements_two[2]} />
              <div class="diagram" bind:this={dia_elements_two[3]} />
            </div>
          </div>
        </div>
        <hr />
        <div class="accuracy">
          <div bind:this={acc_element} />
          <div class="iterations" bind:this={sliderDiv}>
            {#if $metricData && $metricData['iterations']}
              <Slider
                bind:value={sliderValue}
                on:click={() => {
                  if (sliderValue !== currentIteration) currentIteration = sliderValue
                }}
                min={1}
                max={$metricData['iterations'].length}
                step={stepSize}
                discrete
                tickMarks
                input$aria-label="Tick slider"
              />
              <div class="iteration-input">
                <Input
                  label="Iteration"
                  bind:value={inputValue}
                  type="number"
                  min="1"
                  max={$metricData['iterations'].length}
                />
                <ion-icon
                  name="checkmark-circle-outline"
                  style="width: 100%; height: 100%; cursor: pointer;"
                  on:click={() => {
                    if (inputValue > $metricData['iterations'].length) inputValue = $metricData['iterations'].length
                    if (inputValue < 1) inputValue = 1
                    if (inputValue !== currentIteration) currentIteration = inputValue
                  }}
                />
              </div>
            {/if}
          </div>
        </div>
      </div>
    </Card>
  </div>
{/if}

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
  }

  h4 {
    margin: 5px;
  }

  p {
    margin: 5px;
  }

  .dataset-info {
    display: grid;
    grid-template-rows: 1fr 1fr;
    row-gap: 5px;
  }

  .battle {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 50px;
  }
  .process {
    display: grid;
    grid-template-rows: auto 4em 280px 4em 1fr;
  }

  .process-info,
  .sample {
    padding: 0 2em;
  }

  .sample {
    display: flex;
    flex-direction: column;
    row-gap: 1em;
    justify-content: space-between;
  }

  .data {
    overflow: auto;
    display: flex;
    flex-direction: row;
    column-gap: 5px;
  }

  .sample-navigation {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
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
    display: grid;
    grid-template-columns: 1fr 120px;
    align-items: center;
  }

  .metrics {
    border: 1px solid lightgray;
  }

  .heading {
    width: 100%;
    display: flex;
    align-items: center;
    writing-mode: vertical-lr;
    transform: rotate(-180deg);
    font-weight: normal;
    padding: 5px 0;
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
    /* max-width: 250px; */
  }

  .span2 {
    grid-column: span 2;
    max-width: 350px;
  }

  ion-icon {
    cursor: pointer;
    font-size: 28px;
  }

  .iteration-input {
    display: grid;
    grid-template-columns: 85px 1fr;
    column-gap: 5px;
    align-items: center;
  }
</style>
