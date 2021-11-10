<script>
  import { onMount } from 'svelte'
  import axios from 'axios'
  import Image from './Image.svelte'
  import Select from '../../../../ui/Select.svelte'
  import Button from '../../../../ui/Button.svelte'
  import Card from '../../../../ui/Card.svelte'
  import { router } from 'tinro'
  import { data as datasets } from '../../../../store/datasets'
  import { loadSample, samples_to_label, addLabel } from '../../../../store/samples'

  export let sampleCount = 9

  const { id } = router.params()
  let dataset, labels, ready
  let samples = []
  let chosen = {}

  $: dataset = $datasets[id]
  $: ready = dataset && samples.length !== 0
  $: if (ready) labels = dataset.labels

  onMount(() => {
    loadAndSetSamples()
    // Remove empty entries (caused by backend error) from array
    // samples = samples.filter((el) => el != null)
  })

  async function loadAndSetSamples() {
    // Fill samples until sampleCount
    if ($samples_to_label.length < sampleCount) {
      const neededSamples = sampleCount - $samples_to_label.length
      for (let i = 0; i < neededSamples; i++) {
        console.debug('Loading sample...', i + 1)
        const newSample = await loadSample(id)
        updateSampleList(newSample)
      }
      samples = $samples_to_label
      for (const sample of samples) {
        chosen[sample.id] = false
      }
    }
  }

  function updateSampleList(newSample) {
    $samples_to_label = [...$samples_to_label, newSample]
  }

  async function send(label_id) {
    if (Object.values(chosen).some((bool) => bool === true)) {
      const sample_ids_to_remove = []

      /**
       * TODO: There is a delay of some seconds every time a label is sent
       * to the server. That's pain.
       * Anyway, not awaiting it can cause issues, as we've seen in the past.
       * We should find a way to send the requests sequentially, but allow the
       * user to rush through all the samples as fast as he wants.
       * If he finishes before everything is loaded, it's no problem, but just
       * remove the delay in the labeling process.
       *
       */

      // Send label, save new sample in store
      for (const [sample_id, isChosen] of Object.entries(chosen)) {
        if (isChosen) {
          const newSample = await addLabel(sample_id, label_id)
          updateSampleList(newSample)
          sample_ids_to_remove.push(sample_id)
          // Remove entry of chosen object
          delete chosen[sample_id]
        }
      }

      // Remove chosen from samples
      samples = samples.filter((sample) => !sample_ids_to_remove.includes(sample.id.toString(10)))

      // Remove it also from store
      $samples_to_label = $samples_to_label.filter((sample) => !sample_ids_to_remove.includes(sample.id.toString(10)))

      // If samples are all labeled, set next samples
      if (samples.length === 0) {
        if ($samples_to_label.length < sampleCount) {
          loadAndSetSamples()
        } else {
          samples = $samples_to_label
        }
      }
    } else {
      console.debug('Before you can send a label, please select according samples by clicking on it.')
    }
  }
</script>

{#if ready}
  <Card>
    <div class="wrapper">
      <div class="mw9 center ph3-ns">
        <div class="cf ph2-ns">
          {#each samples as sample, i}
            {#if sample}
              <div
                id="sample{i}"
                class="fl w-100 w-third-ns pa2 samples"
                on:click={() => (chosen[sample.id] = !chosen[sample.id])}
              >
                <div class="select-wrapper" class:chosen={chosen[sample.id]}>
                  <Image data={sample.content} />
                </div>
              </div>
            {/if}
          {/each}
        </div>
        <div class="labels">
          {#each labels as { id, name }, i (id)}
            <Button small on:click={() => send(id)}>{name} <code>{i + 1}</code></Button>
          {/each}
        </div>
      </div>
    </div>
  </Card>
{/if}

<style>
  .chosen {
    background-color: var(--clr-primary-light-alt);
  }

  .select-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 8.5em;
    width: 8.5em;
  }

  .wrapper {
    display: flex;
    flex-direction: row;
  }

  ul {
    padding: 0;
    margin: 0;
    width: 150px;
  }

  .samples {
    display: grid;
    justify-content: center;
    margin: 8px;
    border-radius: 10px;
  }

  .w-third-ns {
    width: 30.33333%;
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
