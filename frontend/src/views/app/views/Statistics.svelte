<script>
  import Chartkick from 'chartkick'
  import Chart from 'chart.js'
  import { onMount } from 'svelte'
  import { router } from 'tinro'

  const { id } = router.params()

  let classStats = [{
    name: 'dog',
    total: 1500,
    labeled: 1023
  }, {
    name: 'cat',
    total: 1000,
    labeled: 343
  }, {
    name: 'fish',
    total: 7200,
    labeled: 3423
  }, {
    name: 'car',
    total: 400,
    labeled: 312
  }, {
    name: 'horse',
    total: 600,
    labeled: 23
  }, {
    name: 'plane',
    total: 1100,
    labeled: 189
  }]

  let userStats = {
    total: 13205,
    labeled: 2000
  }

  let classCharts = []
  let pieCharts = []

  onMount(() => {
    Chartkick.use(Chart)
    classCharts.forEach((chart, index) => {
      new Chartkick.BarChart(chart, [['Unlabeled', classStats[index].total - classStats[index].labeled], ['Labeled', classStats[index].labeled]])
    })
  })
</script>

<style>

</style>

<h1 class="mb4">Dataset {id} - Statistics</h1>
<h2 class="mb4">Chartkick</h2>
{#each classStats as stat, i}
  <div class="fl w-third pa2">
    <h3 class="mb4">{stat.name}</h3>
    <div bind:this={classCharts[i]} style="height: 250px;"></div>
  </div>
{/each}
