<script>
  import { onMount } from 'svelte'
  import axios from 'axios'
  import Image from './Image.svelte'
  import Select from '../../../../ui/Select.svelte'
  import Button from '../../../../ui/Button.svelte'
  import Card from '../../../../ui/Card.svelte'
  import { router } from 'tinro'
  import { data as datasets } from '../../../../store/datasets'
  import Table from './Table.svelte'
  import Input from '../../../../ui/Input.svelte'

  export let sampleCount = 9

  const mappings = {
    table: Table,
    image: Image
  }

  const { id } = router.params()
  let dataset, labels, ready
  let samples = []

  $: dataset = $datasets[id]
  $: ready = dataset
  // $: ready = dataset && samples.length !== 0
  $: if (ready) labels = dataset.labels

  onMount(() => {
    /*
    axios({
      method: 'get',
      url: `/datasets/${id}/samples`,
      params: {
        page: 0,
        limit: 3,
        labeled: true
      }
    })
      .then(response => {
        console.log(response)
      })
      .catch(err => console.log(err))
    // Remove empty entries (caused by backend error) from array
    samples = samples.filter(el => el != null)

     */
  })

  // Filter html elements
  let selectElements = {}

  // Select options
  let filterOptions

  $: if (ready) filterOptions = [
    { name: 'Label', label: 'labels', options: labels.map(label => label.name) },
    { name: 'User', label: 'users', options: ['Lisa', 'Mona', 'Petra'] },
    { name: 'Divided  labels', label: 'divided_labels', options: ['True', 'False'] }
  ]

  onMount(() => {
    filterData({})
  })

  async function filterData(params) {
    console.log('SE', selectElements)
    console.log(samples)
    samples = []
    await axios({
      method: 'get',
      url: `/datasets/${id}/samples`,
      params: {
        page: 0,
        limit: 3,
        labeled: true,
        ...params
      }
    })
      .then(response => {
        samples.push(...response.data)
        // Remove empty entries (caused by backend error) from array
        // samples = samples.filter(el => el != null)
        samples = [...samples]
      })
      .catch(err => console.log(err))
  }

  async function send(sample_id, label_id) {
    await axios({
      method: 'post',
      url: `/samples/${sample_id}`,
      params: {
        label_id
      }
    })
      .then(res => {
        // Do something with next sample
      })
      .catch(err => console.log(err))
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

{#if ready}
  <Card>
    <div class="wrapper">
      <div class="menu">
        <ul>
          {#each filterOptions as filterOption, i}
            <Select bind:value={selectElements[filterOption.label]} emptyFirst={true} label={filterOption.name}
                    values={filterOption.options} />
          {/each}
          <Input bind:value={selectElements["free_text"]} type="text" label="Free text" />
        </ul>
        <Button label="Filter" on:click={() => {filterData(selectElements)}} />
      </div>
      <div class="mw9 center ph3-ns">
        <div class="cf ph2-ns">
          {#each samples as sample}
            {#if sample}
              <div class="fl w-100 w-third-ns pa2 samples">
                {#if Object.keys(mappings).includes(sample.type)}
                  <svelte:component this={mappings[sample.type]} data={sample.content} toDecode={false}/>
                {:else}
                  <p>Unsupported type {sample.type}</p>
                {/if}
              </div>
            {/if}
          {/each}
        </div>
      </div>
    </div>
  </Card>
{/if}
