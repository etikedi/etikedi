<script>
  import Chartkick from 'chartkick'
  import Chart from 'chart.js'
  import ApexCharts from 'apexcharts'
  import { onMount } from 'svelte'
  import { router } from 'tinro'

  const { id } = router.params()

  let options = {
    chart: {
      type: 'line'
    },
    series: [{
      name: 'sales',
      data: [30,40,35,50,49,60,70,91,125]
    }],
    xaxis: {
      categories: [1991,1992,1993,1994,1995,1996,1997, 1998,1999]
    }
  }

  onMount(() => {
    Chartkick.use(Chart)

    new Chartkick.LineChart("chart-1", {"2017-01-01": 11, "2017-01-02": 6})

    let chart = new ApexCharts(document.querySelector("#chart"), options);

    chart.render();
  })
</script>

<style>
    #chart {
        max-width: 650px;
        margin: 35px auto;
    }
</style>

<h1 class="mb4">Dataset {id} - Statistics</h1>
<h2 class="mb4">Chartkick</h2>
<div id="chart-1" style="height: 300px;"></div>
<h2 class="mb4">ApexCharts</h2>
<div id="chart"></div>