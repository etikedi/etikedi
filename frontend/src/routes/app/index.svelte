<script>
  import { onMount } from 'svelte'

  import { datasets } from '../../store'

  const { data, load } = datasets

  onMount(() => {
    load()
  })
</script>

<h1>App</h1>

{#each $data as dataset}
  <div>{JSON.stringify(dataset)}</div>
{/each}
