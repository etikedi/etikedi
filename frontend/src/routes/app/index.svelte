<script>
  import { onMount } from 'svelte'

  import DatasetPreview from '../../components/DatasetPreview.svelte'
  import { data, load } from '../../store/datasets'

  onMount(() => {
    load()
  })
</script>

<style>
    .header {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1em;
    }

    h1 {
        margin: 0;
    }
</style>

<div class="header">
  <h1>Datasets</h1>
  <a href="/app/upload">
    <button class="btn btn-lg"> Add one </button>
  </a>
</div>

{#each $data as dataset}
  <DatasetPreview {dataset} />
{/each}
