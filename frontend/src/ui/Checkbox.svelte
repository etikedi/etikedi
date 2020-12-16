<script lang="ts">
  export let value: any
  export let label: string = ''
  export let disabled = false

  //$: name = value ? 'checkmark-sharp' : 'close-sharp'
  $: name = value ? 'close-sharp' : 'checkmark-sharp'
</script>

<style>
  label {
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

  label:hover,
  label:focus {
    box-shadow: 0 0.1em 0.5em #00000010;
    border-color: var(--clr-primary-light-alt);
  }

  label.disabled {
    opacity: 0.75;
  }

  input {
    display: none;
  }

  ion-icon {
    transform: scale(1.5) translateY(0.1em);
    margin-right: 0.75em;
  }
</style>

<div class="mb3">
  <label class:disabled>
    <ion-icon {name} />
    {label}
    <input type="checkbox" {...$$restProps} {disabled} bind:checked={value} />
  </label>
</div>
