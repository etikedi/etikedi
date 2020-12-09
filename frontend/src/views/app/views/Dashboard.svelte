<script>
  import DatasetPreview from './DatasetPreview.svelte'

  import { data } from '../../../store/datasets'
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
  <a href="/app/upload"> <button class="btn btn-lg"> Add one </button> </a>
</div>

{#each Object.values($data) as dataset}
  <DatasetPreview {dataset} />
{/each}
