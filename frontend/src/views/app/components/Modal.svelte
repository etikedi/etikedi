<script lang="ts">
  import Button from '../../../ui/Button.svelte'
  import { createEventDispatcher, getContext } from 'svelte'
  import { terminate_experiment } from '../../../store/al-war'
  const dispatch = createEventDispatcher()
  const { close } = getContext('simple-modal')

  export let label = "It's a modal!"
  export let button = ['Yes', 'Continue with training']
</script>

<div>
  {label}
  {#if button}
    <div class="buttons">
      <Button
        label={button[0]}
        on:click={() => {
          $terminate_experiment = true
          close()
        }}
      />
      <Button label={button[1]} on:click={() => close()} />
    </div>
  {/if}
</div>

<style>
  div {
    display: flex;
    flex-direction: column;
    row-gap: 10px;
    align-items: center;
  }

  .buttons {
    display: flex;
    flex-direction: row;
    column-gap: 20px;
  }
</style>
