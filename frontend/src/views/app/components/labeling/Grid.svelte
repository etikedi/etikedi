<script>
  import { onMount } from 'svelte'
  import axios from 'axios'
  import Image from './Image.svelte'
  import Select from '../../../../ui/Select.svelte'
  import Button from '../../../../ui/Button.svelte'
  import Card from '../../../../ui/Card.svelte'

  export let displayed = [
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Dog' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Mona', label: 'Dog' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Petra', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Mouse' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Petra', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Petra', label: 'Mouse' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Mona', label: 'Cat' }
  ]

  export let labels = []
  export let datasetId

  let samples = []
  let ready = false

  onMount(() => {
    for (let i = 0; i < 9; i++) {
      axios({
        method: 'get',
        url: `/datasets/${datasetId}/first_sample`
      })
        .then(response => {
          samples[i] = response.data
        })
        .catch(err => {
          // Remove failed sample
          samples.splice(i, 1)
        })
    }
    console.log(samples)
    ready = true
  })

  /* Filtering */
  let filterOptions
  let selectFilter = {}

  filterOptions = [
    { name: 'Label', label: 'label', options: labels.map(label => label.name) },
    { name: 'User', label: 'user', options: ['Lisa', 'Mona', 'Petra'] },
    { name: 'Uncertainty', label: 'uncertainty', options: ['Equal', 'Different'] },
    { name: 'Already checked', label: 'checked', options: ['Yes', 'No'] }
  ]

  function filterData() {
    let array = []
    Object.keys(selectFilter).forEach(key => {
      if (selectFilter[key]) {
        array.push(displayed.filter(sample => sample[key] === selectFilter[key]))
      }
    })
    array = array.flat()
    // Eliminate duplicates and convert it back to array
    displayed = [...new Set([...array])]
  }

  let chosen = []

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
    const newSamples = []
    console.log('Label', label_id)
    console.log('samples', chosen)
    for (const sample of chosen) {
      newSamples.push(await axios({
        method: 'post',
        url: `/samples/${sample.id}`,
        params: {
          label_id
        }
      }))
    }
    console.log(newSamples)
  }

</script>

<style>
    .wrapper {
        display: flex;
        flex-direction: row;

    }

    .menu {
        display: flex;
        flex-direction: column;
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
</style>

<Card>
  <div class="wrapper">
    <div class="menu">
      <ul>
        {#each filterOptions as filterOption, i}
          <Select bind:value={selectFilter[filterOption.label]} emptyFirst={true} label={filterOption.name}
                  values={filterOption.options} />
        {/each}
      </ul>
      <Button label="Filter" on:click={filterData} />
    </div>
    <div class="mw9 center ph3-ns">
      <div class="cf ph2-ns">
        {#if ready}
          {#each samples as sample, i}
            {#if sample}
              <div id="sample{i}" class="fl w-100 w-third-ns pa2 samples" on:click={() => choose(sample, i)}>
                <Image data={sample.content} />
              </div>
            {/if}
          {/each}
        {/if}
      </div>
    </div>
  </div>
  <div class="labels">
    {#each labels as { id, name }, i (id)}
      <Button small on:click={() => send(id)}>{name} <code>{i + 1}</code></Button>
    {/each}
  </div>
</Card>

