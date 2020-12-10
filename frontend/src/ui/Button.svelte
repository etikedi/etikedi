<script lang="ts">
  export let label: string = ''
  export let icon: string | null = null
  export let full = false
  export let small = false
</script>

<style>
  button {
    display: inline-block;
    padding: 0.75em 1.5em;
    background-color: var(--clr-white);
    border-radius: var(--round);
    border: 2px solid var(--clr-primary-light);
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    cursor: pointer;
  }

  button:hover,
  button:focus {
    box-shadow: 0 0.1em 0.5em #00000010;
    border-color: var(--clr-primary-light-alt);
  }

  button.full {
    width: 100%;
    display: block;
  }

  button.small {
    font-size: 0.8em;
  }

  ion-icon {
    font-size: 1em;
    transform: translateY(0.1em) scale(1.75);
    margin-right: 0.5em;
  }
</style>

<button class:full class:small {...$$restProps} on:click>
  {#if icon}
    <ion-icon name={icon} />
  {/if}
  {label}
  <slot />
</button>
