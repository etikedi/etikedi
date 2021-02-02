<script>
  import Chartkick from 'chartkick'
  import Chart from 'chart.js'
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import { data as datasets } from '../../../store/datasets'
  import axios from 'axios'

  const { id } = router.params()

  let dataset, labels, ready, stats

  $: dataset = $datasets[id]
  $: ready = dataset

  let classCharts = []
  let pieCharts = []
  let userChart, distPie, distBar, classDistPie, classDistBar

  $: if (ready) {
    labels = dataset.labels
    stats = dataset.statistics
  }

  onMount(() => {
    axios({
      method: 'get',
      url: `/datasets/${id}/metrics`
    })
      .then(response => console.log(response))
    Chartkick.use(Chart)
    let labelDist = []
    labelDist.push(['labeled', stats.labelled_samples])
    labelDist.push(['features', stats.features])
    labelDist.push(['unlabeled', stats.total_samples - stats.features - stats.labelled_samples])
    new Chartkick.PieChart(classDistPie, labelDist, { legend: 'bottom', donut: true })
    new Chartkick.BarChart(classDistBar, labelDist)
  })

</script>

<style>
    .graph {
        height: 250px;
    }
</style>

{#if ready}
  <h1 class="mb4">Dataset {id} - Statistics</h1>
  <h2 class="mb4">Data distribution</h2>
  <h3 class="mb4">Total samples: {stats.total_samples}</h3>
{/if}
<div class="fl w-50 pa2">
  <div class="graph" bind:this={classDistPie}></div>
</div>
<div class="fl w-50 pa2">
  <div class="graph" bind:this={classDistBar}></div>
</div>
