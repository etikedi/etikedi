<script>
  import { onMount } from 'svelte'

  import { datasets, load } from '../../store/datasets'

  onMount(() => {
    load()
  })
</script>

<h1>App</h1>

{#each $datasets as dataset}
  <div>{JSON.stringify(dataset)}</div>
{/each}
