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
    labeled: 2014
  }, {
    name: 'car',
    total: 400,
    labeled: 312
  }, {
    name: 'horse',
    total: 600,
    labeled: 701
  }, {
    name: 'plane',
    total: 1100,
    labeled: 189
  }]

  let userStats = [['Automatically', 10000], ['Peter', 712], ['Josh', 38], ['Steve', 404], ['Maria', 841], ['Sophie', 31]]

  let classCharts = []
  let pieCharts = []
  let userChart, distPie, distBar, classDistPie, classDistBar

  onMount(() => {
    Chartkick.use(Chart)
    new Chartkick.PieChart(classDistPie, classStats.map(el => {
      return [el.name, el.labeled]
    }))
    new Chartkick.BarChart(classDistBar, classStats.map(el => {
      return [el.name, el.labeled]
    }))
    classCharts.forEach((chart, index) => {
      new Chartkick.BarChart(chart, [['Unlabeled', classStats[index].total - classStats[index].labeled], ['Labeled', classStats[index].labeled]])
    })
    new Chartkick.PieChart(distPie, userStats)
    new Chartkick.BarChart(distBar, userStats.filter(el => el[0] !== 'Automatically'))
  })
</script>

<style>

</style>

<h1 class="mb4">Dataset {id} - Statistics</h1>
<h2 class="mb4">Class information</h2>
<h3 class="mb4">Totally labeled</h3>
<div class="fl w-50 pa2">
  <div bind:this={classDistPie} style=" height: 250px;"></div>
</div>
<div class="fl w-50 pa2">
  <div bind:this={classDistBar} style="height: 250px;"></div>
</div>
<h3 class="mb4">Labeled data per class</h3>
{#each classStats as stat, i}
  <div class="fl w-third pa2">
    <h3 class="mb4">{stat.name}</h3>
    <div bind:this={classCharts[i]} style="height: 250px;"></div>
  </div>
{/each}
<h2 class="mb4">Label distribution</h2>
<div class="fl w-50 pa2">
  <h3 class="mb-4">Including labeled by system</h3>
  <div bind:this={distPie} style="height: 250px;"></div>
</div>
<div class="fl w-50 pa2">
  <h3 class="mb-4">Only by users</h3>
  <div bind:this={distBar} style="height: 250px;"></div>
</div>
