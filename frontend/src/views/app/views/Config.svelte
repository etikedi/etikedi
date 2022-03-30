<script lang="ts">
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import { sentenceCase } from 'change-case'
  import { notifier } from '@beyonk/svelte-notifications'

  import Button from '../../../ui/Button.svelte'
  import Input from '../../../ui/Input.svelte'
  import Checkbox from '../../../ui/Checkbox.svelte'
  import Select from '../../../ui/Select.svelte'

  import { data, remove, loading as loadingDatasets } from '../../../store/datasets'
  import { get, save, loading as loadingConfig, ALConfig } from '../../../store/config'
  import { BMDRConfig } from '../../../lib/al_configs'

  const { id } = router.params()

  export let alWar = false
  export let config = {}
  export let strategySchema = null
  export let strategyDefinitions = null
  export let name

  let spec

  // Set schema initial
  if (!alWar) spec = ALConfig
  else if (alWar && strategySchema) {
    config = {}
    spec = { ...strategySchema }
  }

  $: dataset = $data[id]
  $: loading = $loadingConfig || $loadingDatasets

  onMount(async () => {
    if (!alWar) config = await get(id)
    else prepareSchema()
  })

  function prepareSchema() {
    for (const key of Object.keys(spec)) {
      // Set default values
      if (strategySchema[key]['default']) {
        config[key] = strategySchema[key]['default']
      }

      // Set select options
      if (strategySchema[key]['allOf'] && strategyDefinitions) {
        const ref = strategySchema[key]['allOf'][0]['$ref'].split('/')
        const definitionKey = ref[ref.length - 1]
        const values = strategyDefinitions[definitionKey]['enum']
        spec[key]['type'] = values
      }

      // TODO: min, max, steps, ...
    }
  }

  async function submit() {
    try {
      await save(id, config)
      notifier.success('Saved')
    } catch (e) {
      console.error(e)
      notifier.danger(e.message)
    }
  }

  async function del() {
    try {
      await remove(id)
      notifier.success('Deleted')
      back()
    } catch (e) {
      console.error(e)
      notifier.danger(e.message)
    }
  }

  function back() {
    router.goto('../../')
  }
</script>

<div>
  {#if !alWar}
    <Button icon="arrow-back-circle-sharp" label="Back" on:click={back} />
  {/if}
  <br />
  {#if dataset && config}
    <h2><b>{name ?? dataset.name}</b> Config</h2>
    <form on:submit|preventDefault={submit}>
      {#each Object.entries(spec) as [key, { type, ...props }]}
        {#if type === 'number'}
          <Input {type} {...props} bind:value={config[key]} disabled={loading} label={sentenceCase(key)} />
        {:else if Array.isArray(type)}
          <Select label={sentenceCase(key)} bind:value={config[key]} disabled={loading} values={type} />
        {:else if type === 'bool'}
          <Checkbox bind:value={config[key]} disabled={loading} label={sentenceCase(key)} />
        {/if}
      {/each}
      {#if !alWar}
        <Button type="submit" {loading} disabled={loading} label="Update" icon="checkmark-circle-sharp" />
      {:else}
        <!--
        <h3>Query Strategy Config</h3>
        {#each Object.entries(StrategyConfig) as [key, { type, ...props }]}
          {#if type === 'number'}
            <Input {type} {...props} bind:value={strategyConfig[key]} disabled={loading} label={sentenceCase(key)} />
          {:else if Array.isArray(type)}
            <Select label={sentenceCase(key)} bind:value={strategyConfig[key]} disabled={loading} values={type} />
          {:else if type === 'bool'}
            <Checkbox bind:value={strategyConfig[key]} disabled={loading} label={sentenceCase(key)} />
          {/if}
        {/each}
        -->
      {/if}
    </form>
    <br />
    {#if !alWar}
      <Button
        on:click={del}
        danger
        label="Delete dataset and all the trained data"
        icon="remove-circle-sharp"
        {loading}
        disabled={loading}
      />
    {/if}
  {:else}
    <div class="text-center">
      <div class="loading loading-lg" />
      <p>Waiting for server</p>
    </div>
  {/if}
</div>
