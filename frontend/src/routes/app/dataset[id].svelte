<script context="module">
  export function preload(page) {
    return { id: page.params.id }
  }
</script>
<script>
  import { onMount } from 'svelte'
  import { data as datasets } from '../../store/datasets'
  import { data as sample, loadSample, putLabel } from '../../store/samples'

  export let id
  let newLabel
  let dataset = $datasets.find(el => el.id == id)

  onMount(() => {
    loadSample(id)
  })

  function send() {
    putLabel(sample.id, newLabel.id)
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

{#if dataset}
  <h1>Dataset {id}</h1>
  <div class="card mb-2 container">
    <img src="https://picsum.photos/200">
    <label for="label">Label</label>
    <select bind:value={newLabel} id="label">
      {#each dataset.labels as label}
        <option value={label}>
          {label.name}
        </option>
      {/each}
    </select>
    <button class="" on:click={send}>
      Send
    </button>
  </div>
{:else}
  <p>Please fetch the datasets first:</p>
  <a href="/app">APP</a>
{/if}