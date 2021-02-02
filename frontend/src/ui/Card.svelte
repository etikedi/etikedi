<script lang="ts">
  export let disabled = false
</script>

<div class:disabled class="mb2">
  <slot />
</div>

<style>
  div {
    width: 100%;
    padding: 1em;
    border-radius: var(--round);
    border: 2px solid var(--clr-primary-light);
    background-color: var(--clr-white);
  }

  div.disabled {
    filter: brightness(0.95);
  }
</style>
