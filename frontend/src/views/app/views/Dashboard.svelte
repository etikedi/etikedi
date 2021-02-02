<script>
  import Button from '../../../ui/Button.svelte'
  import DatasetPreview from './DatasetPreview.svelte'

  import { data } from '../../../store/datasets'
  import { isAdmin } from '../../../store/me'
</script>

{#if $isAdmin}
  <a href="/app/users/">
    <Button label="User management" icon="people-circle-sharp" />
  </a>
{/if}

<div class="flex justify-between items-center mb3">
  <h1>Datasets</h1>
  <a href="/app/upload">
    <Button label="Add one" icon="add-circle-sharp" />
  </a>
</div>

{#each Object.values($data) as dataset}
  <DatasetPreview {dataset} />
{/each}
