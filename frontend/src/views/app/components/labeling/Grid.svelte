<script>
  import { onMount } from 'svelte'
  import axios from 'axios'
  import Image from './Image.svelte'
  import Select from '../../../../ui/Select.svelte'
  import Button from '../../../../ui/Button.svelte'
  import Card from '../../../../ui/Card.svelte'
  import { router } from 'tinro'
  import { data as datasets } from '../../../../store/datasets'

  export let sampleCount = 9

  const { id } = router.params()
  let dataset, labels, ready
  let samples = []

  $: dataset = $datasets[id]
  $: ready = dataset && samples.length !== 0
  $: if (ready) labels = dataset.labels

  onMount(() => {
    // Load 9 unlabeled samples
    for (let i = 0; i < sampleCount; i++) {
      axios({
        method: 'get',
        url: `/datasets/${id}/first_sample`
      })
        .then(response => {
          samples[i] = response.data
        })
        .catch(err => console.log(err))
    }
    // Remove empty entries (caused by backend error) from array
    samples = samples.filter(el => el != null)
  })

  let chosen = []
  let nextSamples = []

  function choose(sample, index) {
    if (chosen.find(el => el === sample)) {
      chosen.splice(chosen.indexOf(sample), 1)
      document.getElementById(`sample${index}`).style.backgroundColor = 'initial'
      return
    }
    document.getElementById(`sample${index}`).style.backgroundColor = 'lightskyblue'
    chosen.push(sample)
  }

  async function send(label_id) {

    // Remove empty entries in array
    samples = samples.filter(el => el != null)

    const temp = samples

    // Remove background color
    samples.forEach((sample, index) => {
      document.getElementById(`sample${index}`).style.backgroundColor = 'initial'
    })

    // Remove chosen from samples
    chosen.forEach(el => {
      temp.splice(temp.indexOf(el), 1)
    })

    samples = temp

    // Send
    for (const [index, sample] of chosen.entries()) {
      await axios({
        method: 'post',
        url: `/samples/${sample.id}`,
        params: {
          label_id
        }
      })
        .then(res => {

          // Save next sample
          nextSamples.push(res.data)
        })
        .catch(err => console.log(err))
    }
    chosen = []

    // If samples are all labeled, set next samples
    if (Object.values(samples).length === 0) {
      if (nextSamples.length < sampleCount) {

        // Load missing samples
        for (let i = 0; i < sampleCount - nextSamples.length; i++) {
          await axios({
            method: 'get',
            url: `/datasets/${id}/first_sample`
          })
            .then(response => {
              nextSamples.push(response.data)
            })
            .catch(err => console.log(err))
        }
      }
      samples = nextSamples
      nextSamples = []
    }
  }

</script>

<style>
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

{#if ready}
  <Card>
    <div class="wrapper">
      <div class="mw9 center ph3-ns">
        <div class="cf ph2-ns">
          {#each samples as sample, i}
            {#if sample}
              <div id="sample{i}" class="fl w-100 w-third-ns pa2 samples" on:click={() => choose(sample, i)}>
                <Image data={sample.content} />
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
