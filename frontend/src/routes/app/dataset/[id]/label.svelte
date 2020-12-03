<script context="module">
  export function preload(page) {
    return page.params
  }
</script>

<script>
  import { onMount } from 'svelte'
  import axios from 'axios'

  import { data as datasets } from '../../../../store/datasets'

  export let id

  let assigned
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
    console.log(sample.id, assigned.id)
    const { data } = await axios({
      method: 'post',
      url: `/samples/${sample_id}`,
      data: {
        sample_id: sample.id,
        label_id: assigned.id,
      },
    })
    console.log(data)
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
    <img src="https://picsum.photos/200" />
    <label for="label">Label</label>
    <select bind:value={assigned} id="label">
      {#each dataset.labels as label}
        <option value={label}>{label.name}</option>
      {/each}
    </select>
    <button on:click={send}>Send</button>
  </div>
{:else}Loading Sample...{/if}
