<script context="module">
  export function preload(page) {
    return page.params
  }
</script>

<script>
  import { onMount } from 'svelte'
  import axios from 'axios'

  import Table from '../../../../components/labeling/Table.svelte'
  import Image from '../../../../components/labeling/Image.svelte'

  import { data as datasets } from '../../../../store/datasets'

  const mappings = {
    table: Table,
    image: Image,
  }

  export let id

  let error = null
  let assigned = null
  let sample = null

  $: dataset = $datasets[id]
  $: ready = dataset && sample != null

  onMount(async () => {
    const { data } = await axios({
      method: 'get',
      url: `/datasets/${id}/first_sample`,
    })
    sample = data
  })

  async function send() {
    console.log(sample.id, assigned)
    if (assigned === null) {
      error = 'Select a label'
      return
    }
    const id = sample.id
    sample = null
    const { data } = await axios({
      method: 'post',
      url: `/samples/${id}`,
      params: {
        label_id: assigned,
      },
    })
    error = null
    assigned = null
    sample = data
  }
</script>

<style>
  .card {
    padding: 30px;
    border-radius: 15px;
    border: 2px solid #032557;
    align-items: center;
  }
</style>

{#if ready}
  <h1>Dataset {id}</h1>
  <div class="card mb-2 container">
    {#if Object.keys(mappings).includes(sample.type)}
      <svelte:component this={mappings[sample.type]} data={sample.content} />
    {:else}
      <p>Unsupported type {sample.type}</p>
    {/if}
    <!-- {#if sample.type === 'image'}
      <img src="data:image/png;base64,{sample.content}" alt="sample" />
    {:else if sample.type === 'table'}
      {@html atob(sample.content)}
    {:else}{sample.type}{/if} -->
    <label for="label">Label</label>
    <select bind:value={assigned} id="label">
      {#each dataset.labels as { id, name } (id)}
        <option value={id}>{name}</option>
      {/each}
    </select>
    {#if error}
      <p>{error}</p>
    {/if}
    <button on:click={send}>Send</button>
  </div>
{:else}Loading Sample...{/if}
