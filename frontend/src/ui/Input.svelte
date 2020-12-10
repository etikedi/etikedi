<script lang="ts">
  export let value: any
  export let label: string = ''
</script>

<style>
  input {
    width: 100%;
    display: block;
    padding: 1em;
    border-radius: var(--round);
    border: 2px solid var(--clr-primary-light);
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    box-sizing: border-box;
    background-color: var(--clr-white);
  }

  input:hover,
  input:focus {
    box-shadow: 0 0.1em 0.5em #00000010;
    border-color: var(--clr-primary-light-alt);
  }

  input:disabled {
    opacity: 0.75;
  }
</style>

<div class="mb3"><label> {label} <input {...$$restProps} bind:value /> </label></div>
