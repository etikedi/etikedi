<script>
  import { onMount } from 'svelte'

  import DatasetPreview from '../../components/DatasetPreview.svelte'
  import { datasets } from '../../store'

  const { data, load } = datasets

  onMount(() => {
    load()
  })
</script>

<h1>App</h1>

{#each $data as dataset}
  <DatasetPreview {dataset} />
{/each}
