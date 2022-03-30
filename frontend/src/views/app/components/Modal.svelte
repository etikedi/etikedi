<script lang="ts">
  import Button from '../../../ui/Button.svelte'
  import { createEventDispatcher } from 'svelte'
  const dispatch = createEventDispatcher()

  export let label = "It's a modal!"
  export let button = ''
</script>

<div>
  {label}
  {#if button}
    <Button label={button} on:click={() => dispatch('close', { terminate: true })} />
  {/if}
</div>

<style>
  div {
    display: flex;
    flex-direction: column;
    row-gap: 10px;
    align-items: center;
  }
</style>
