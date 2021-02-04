<script>
  import Chartkick from 'chartkick'
  import Chart from 'chart.js'
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import { data as datasets } from '../../../store/datasets'
  import axios from 'axios'

  const { id } = router.params()

  let dataset, labels, ready, stats, rendered

  $: dataset = $datasets[id]
  $: ready = dataset

  let classDistBar
  let labelDist = []
  let loaded = false
  let metrics = []
  let metricGraphs = []

  $: if (ready) {
    labels = dataset.labels
    stats = dataset.statistics
    Chartkick.use(Chart)
    labelDist.push(['labeled', stats.labelled_samples])
    labelDist.push(['unlabeled', stats.total_samples - stats.labelled_samples])
  }

  $: if (ready && rendered) {
    new Chartkick.BarChart(classDistBar, labelDist)
  }

  $: if (loaded) {
    if (metrics.length > 0) {
      metricGraphs.forEach((el, index) => {
        new Chartkick.ScatterChart(metricGraphs[index], metrics[index].values)
      })
    }
  }

  onMount(() => {
    rendered = true
    axios({
      method: 'get',
      url: `/datasets/${id}/metrics`
    })
      .then(response => {
        // Only accept metrics exclusively containing numbers
        for (const key in response.data) {
          if (response.data.hasOwnProperty(key) && !response.data[key].some(isNaN) && !response.data[key].some(el => {
            return el === null
          })) metrics.push({
            // Create value pairs (the index of the value should be the x value)
            name: key, values: response.data[key].map((value, index) => {
              return [index, value]
            })
          })
        }
        loaded = true
      })
  })

</script>

<style>
    .graph {
        height: 250px;
        margin: 30px 0;
    }
</style>

{#if ready}
  <h1 class="mb4">{dataset.name} - Statistics</h1>
  <h3 class="mb4">Total samples: {stats.total_samples}, <br> Features: {stats.features}</h3>
{/if}
<div class="graph" bind:this={classDistBar}></div>
{#if loaded}
  {#if metrics.length > 0}
    <h2 class="mb4">AL Metrics</h2>
  {:else}
    <h3 class="mb4">AL metrics will show up here, if available... Let's keep labelling!</h3>
  {/if}
  {#each metrics as metric, i}
    <h3 class="mb4">Metric name: {metric.name}</h3>
    <div class="graph" bind:this={metricGraphs[i]}></div>
  {/each}
{/if}