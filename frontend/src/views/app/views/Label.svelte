<script lang="ts">
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import axios from 'axios'

  import Button from '../../../ui/Button.svelte'
  import Table from '../components/labeling/Table.svelte'
  import Image from '../components/labeling/Image.svelte'
  import Card from '../../../ui/Card.svelte'
  import Checkbox from '../../../ui/Checkbox.svelte'

  import { data as datasets } from '../../../store/datasets'
  import Grid from '../components/labeling/Grid.svelte'
  import Select from '../../../ui/Select.svelte'

  const mappings = {
    table: Table,
    image: Image
  }

  const { id } = router.params()


  let sample = null
  let grid = false
  let dataset, ready

  $: dataset = $datasets[id]
  $: ready = dataset && sample != null

  let filterOptions
  let selectFilter = {}
  let displayed

  $: if (ready) {
    filterOptions = [
      { name: 'Label', label: 'label', options: dataset.labels },
      { name: 'User', label: 'user', options: ['Lisa', 'Mona', 'Petra'] },
      { name: 'Uncertainty', label: 'uncertainty', options: ['Equal', 'Different'] },
      { name: 'Already checked', label: 'checked', options: ['Yes', 'No'] }
    ]
  }

  function filterData() {
    let array = []
    Object.keys(selectFilter).forEach(key => {
      if (selectFilter[key]) {
        array.push(displayed.filter(sample => sample[key] === selectFilter[key]))
      }
    })
    array = array.flat()
    // Eliminate duplicates and convert it back to array
    displayed = [...new Set([...array])]
  }

  onMount(() => {
    axios({
      method: 'get',
      url: `/datasets/${id}/first_sample`
    }).then((response) => {
      sample = response.data
    })

    window.document.addEventListener('keypress', keyPress)
    return () => {
      window.document.removeEventListener('keypress', keyPress)
    }
  })

  function keyPress(e: KeyboardEvent) {
    const i = parseInt(e.key)
    if (dataset && Number.isInteger(i)) {
      const label = dataset.labels[i - 1]
      if (label) send(label.id)
    }
  }

  async function send(selected: string) {
    if (!ready) return
    console.log(selected)
    const id = sample.id
    sample = null
    const { data } = await axios({
      method: 'post',
      url: `/samples/${id}`,
      params: {
        label_id: selected
      }
    })
    sample = data
  }
</script>

<style>
    .data {
        max-height: calc(100vh - 23em);
        overflow: auto;
    }

    .labels {
        margin-top: 2em;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        flex-wrap: wrap;
    }

    .labels > :global(*) {
        margin: 0.5em;
    }

    .wrapper {
        display: flex;
        flex-direction: row;
    }

    .menu {
        display: flex;
        flex-direction: column;
    }

    ul {
      padding: 0;
    }
</style>

{#if ready}
  <div class="flex justify-between items-center">
    <h1 class="mb4">Dataset {id}</h1>
    <Checkbox bind:value={grid} label="Grid view" />
  </div>

  <div class="wrapper">
    {#if grid}
      <div class="menu">
        <ul>
          {#each filterOptions as filterOption, i}
            <Select bind:value={selectFilter[filterOption.label]} emptyFirst={true} label={filterOption.name} values={filterOption.options} />
          {/each}
        </ul>
        <Button label="Filter" on:click={filterData} />
      </div>
    {/if}
    <Card>
      <div class="data tc">
        {#if Object.keys(mappings).includes(sample.type)}
          {#if grid}
            <Grid firstSample={sample.content} labels={dataset.labels} bind:displayed={displayed} />
          {:else}
            <svelte:component this={mappings[sample.type]} data={sample.content} />
          {/if}
        {:else}
          <p>Unsupported type {sample.type}</p>
        {/if}
      </div>

      <div class="labels">
        {#each dataset.labels as { id, name }, i (id)}
          <Button small on:click={() => send(id)}>{name} <code>{i + 1}</code></Button>
        {/each}
      </div>
    </Card>
  </div>
{:else}
  <div class="text-center">
    <div class="loading loading-lg" />
    <p>Waiting for server</p>
  </div>
{/if}
