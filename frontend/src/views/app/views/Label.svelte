<script lang="ts">
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import axios from 'axios'

  import Table from '../components/labeling/Table.svelte'
  import Image from '../components/labeling/Image.svelte'

  import { data as datasets } from '../../../store/datasets'
  import Grid from '../components/labeling/Grid.svelte'

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
    }).then((response) => (sample = response.data))

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

    .top {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }

    .card {
        padding: 1.5em 2em;
        background-color: #f7f7f7;
        border-radius: var(--round);
        border: 1px solid #e9f2ff;
        align-items: center;
    }

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

    .labels > button {
        margin: 0.5em;
    }
</style>

{#if ready}
  <div class="top">
    <h3>Dataset {id}</h3>
    <div class="form-group">
      <label class="form-switch">
        <input type="checkbox" on:change={(e) => grid = e.target.checked}>
        <i class="form-icon"></i> Grid view
      </label>
    </div>
  </div>
  <div class="card mb-2 container">
    <div class="data">
      {#if Object.keys(mappings).includes(sample.type)}
        {#if grid}
          <Grid firstSample={sample.content} labels={dataset.labels}/>
        {:else}
          <svelte:component this={mappings[sample.type]} data={sample.content} />
        {/if}
      {:else}
        <p>Unsupported type {sample.type}</p>
      {/if}
    </div>

    <div class="labels">
      {#each dataset.labels as { id, name }, i (id)}
        <button class="btn" on:click={() => send(id)}>{name} <code>{i + 1}</code></button>
      {/each}
    </div>
  </div>
{:else}
  <div class="text-center">
    <div class="loading loading-lg" />
    <p>Waiting for server</p>
  </div>
{/if}
