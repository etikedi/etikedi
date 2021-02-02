<script>
  import Button from '../../../../ui/Button.svelte'

  import { load, data, loading } from '../../../../store/users'
  import { onMount } from 'svelte'
  import UserPreview from '../components/UserPreview.svelte'

  onMount(() => {
    load()
  })
</script>

<div class="flex justify-between items-center mb3">
  <h1>Users</h1>
  <a href="/app/users/new">
    <Button label="New user" icon="add-circle-sharp" />
  </a>
</div>

{#if $loading === false}
  {#each $data as user}
    <UserPreview {user} />
    <!-- <div>{JSON.stringify(user)}</div> -->
  {/each}
{:else}
  <div class="loading loading-lg" />
{/if}
