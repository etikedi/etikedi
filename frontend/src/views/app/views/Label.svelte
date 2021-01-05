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

  onMount(() => {
    axios({
      method: 'get',
      url: `/datasets/${id}/first_sample`
    }).then(response => sample = response.data)

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
</style>

{#if ready}
  <div class="flex justify-between items-center">
    <h1 class="mb4">Dataset {id}</h1>
    <Checkbox bind:value={grid} label="Grid view" />
  </div>

  {#if grid}
    <Grid firstSample={sample.content} labels={dataset.labels} datasetId={id} />
  {:else}
    <Card>
      <div class="data tc">
        {#if Object.keys(mappings).includes(sample.type)}
          <svelte:component this={mappings[sample.type]} data={sample.content} />
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
  {/if}

{:else}
  <div class="text-center">
    <div class="loading loading-lg" />
    <p>Waiting for server</p>
  </div>
{/if}