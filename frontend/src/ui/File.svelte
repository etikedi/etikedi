<script lang="ts">
  export let element
  export let label: string
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

  input {
    display: none;
  }

  ion-icon {
    font-size: 4em;
  }
</style>

<div class="mb3">
  <label class="tc">
    <ion-icon name="cloud-upload-sharp" />
    <div>{label}</div>
    <input {...$$restProps} bind:this={element} />
  </label>
</div>
