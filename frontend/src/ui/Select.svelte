<script lang="ts">
  export let value: any
  export let values: any[] = []
  export let label: string = ''
  export let emptyFirst = false
</script>

<style>
    select {
        width: 100%;
        display: block;
        padding: 1em;
        border-radius: var(--round);
        border: 2px solid var(--clr-primary-light);
        outline: none;
        appearance: none;
        -webkit-appearance: none;
        box-sizing: border-box;
    }

    select:hover,
    select:focus {
        box-shadow: 0 0.1em 0.5em #00000010;
        border-color: var(--clr-primary-light-alt);
    }

    div {
        position: relative;
    }

    ion-icon {
        position: absolute;
        right: 0.5em;
        top: 1.4em;
        font-size: 1.75em;
        color: var(--clr-primary-light);
    }

    div:hover ion-icon,
    div:focus ion-icon {
        color: var(--clr-primary-light-alt);
    }
</style>

<div class="mb3">
  <label>
    {label}
    <select {...$$restProps} bind:value on:change>
      {#if emptyFirst}
        <option selected value="{undefined}"></option>
      {/if}
      {#each values as v}
        <option value={v.id || v}>{v.name || v.fullname || v}</option>
      {/each}
    </select>
  </label>
  <ion-icon name="caret-down-circle-sharp" />
</div>
