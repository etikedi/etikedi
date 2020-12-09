<script lang="ts">
  export let disabled: boolean = false
  export let field
  export let config

  const [key, { type, ...props }] = field
</script>

<div class="form-group">
  {#if type === 'number'}
    <label class="form-label">
      {key}
      <input class="form-input" type="number" {...props} bind:value={config[key]} {disabled} />
    </label>
  {:else if Array.isArray(type)}
    <label class="form-label">
      {key}
      <select class="form-select" bind:value={config[key]} {disabled}>
        {#each type as option}
          <option value={option}>{option}</option>
        {/each}
      </select>
    </label>
  {:else if type === 'bool'}
    <label class="form-switch">
      <input type="checkbox" bind:checked={config[key]} {disabled} />
      <i class="form-icon" />
      {key}
    </label>
  {/if}
</div>
