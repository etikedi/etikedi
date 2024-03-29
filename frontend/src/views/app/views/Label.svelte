<script lang="ts">
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import axios from 'axios'
  import { notifier } from '@beyonk/svelte-notifications'

  import Button from '../../../ui/Button.svelte'
  import Table from '../components/labeling/Table.svelte'
  import Image from '../components/labeling/Image.svelte'
  import Card from '../../../ui/Card.svelte'
  import Checkbox from '../../../ui/Checkbox.svelte'

  import { data as datasets } from '../../../store/datasets'
  import Grid from '../components/labeling/Grid.svelte'
  import { addLabel, loadSample, samples_to_label } from '../../../store/samples'

  const mappings = {
    tables: Table,
    image: Image,
    text: Table,
  }

  const { id } = router.params()

  let sample = null
  let grid = false
  let dataset, ready
  let last = null

  $: dataset = $datasets[id]
  $: sample = $samples_to_label[0]
  $: ready = dataset && sample != null

  onMount(() => {
    if (!$samples_to_label || $samples_to_label.length === 0) {
      load()
    }

    window.document.addEventListener('keypress', keyPress)
    return () => {
      window.document.removeEventListener('keypress', keyPress)
    }
  })

  async function load() {
    const newSample = await loadSample(id)
    updateSampleList(newSample)
  }

  function updateSampleList(newSample) {
    $samples_to_label = [...$samples_to_label, newSample]
  }

  function shiftSample() {
    $samples_to_label.shift()
    $samples_to_label = [...$samples_to_label]
  }

  function keyPress(e: KeyboardEvent) {
    const i = parseInt(e.key)
    if (dataset && Number.isInteger(i)) {
      const label = dataset.labels[i - 1]
      if (label) send(label.id)
    }
  }

  async function send(label_id: string) {
    if (!ready) return
    const sample_id = sample.id
    sample = null
    const newSample = await addLabel(sample_id, label_id)
    shiftSample()
    updateSampleList(newSample)
    last = [sample_id, label_id]
  }

  async function undo() {
    try {
      if (!last) return
      const [id, label_id] = last
      await axios({
        method: 'delete',
        url: `/samples/${id}`,
        data: { label_id, all: false },
      })
      notifier.success('Deleted')
    } catch (e) {
      console.error(e)
    } finally {
      last = null
    }
  }
</script>

{#if ready}
  <div class="flex justify-between items-center">
    <h1 class="mb4">Dataset {id}</h1>
    {#if sample.type === 'image'}
      <Checkbox bind:value={grid} label="Grid view" />
    {/if}
  </div>

  {#if grid}
    <Grid />
  {:else}
    <Card>
      <div class="data tc">
        {#if Object.keys(mappings).includes(sample.type)}
          <svelte:component this={mappings[sample.type]} data={sample.content} />
        {:else}
          <p>Unsupported type {sample.type}</p>
        {/if}
      </div>

      <div class="labels">
        {#each dataset.labels as { id, name }, i (id)}
          <Button small on:click={() => send(id)}>{name} <code>{i + 1}</code></Button>
        {/each}
      </div>
    </Card>
  {/if}
{:else}
  <div class="text-center">
    <div class="loading loading-lg" />
    <p>Waiting for server</p>
  </div>
{/if}

{#if last}
  <Button on:click={undo} danger label="Undo last" icon="arrow-undo-circle" />
{/if}

<style>
  .data {
    max-height: calc(100vh - 23em);
    overflow: auto;
  }

  .labels {
    margin-top: 2em;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    flex-wrap: wrap;
  }

  .labels > :global(*) {
    margin: 0.5em;
  }
</style>
