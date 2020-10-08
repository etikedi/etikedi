<script>
  import { onMount } from 'svelte'

  import { datasets, fetch } from '../../store/datasets'

  onMount(() => {
    fetch()
  })
</script>

<h1>App</h1>

{#each $datasets as dataset}
  <div>{JSON.stringify(dataset)}</div>
{/each}
