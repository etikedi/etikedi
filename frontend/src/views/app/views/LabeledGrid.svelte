<script>
  import { onMount } from 'svelte'
  import axios from 'axios'
  import Image from '../components/labeling/Image.svelte'
  import Select from '../../../ui/Select.svelte'
  import Button from '../../../ui/Button.svelte'
  import Card from '../../../ui/Card.svelte'
  import { router } from 'tinro'
  import { data as datasets } from '../../../store/datasets'
  import Table from '../components/labeling/Table.svelte'
  import Input from '../../../ui/Input.svelte'
  import CheckboxList from '../../../ui/CheckboxList.svelte'

  export let sampleCount = 3

  const mappings = {
    table: Table,
    image: Image,
    text: Table
  }

  const { id } = router.params()
  let dataset, labels, ready, filterOptions
  let samples = []
  let filterParams = {}


  $: dataset = $datasets[id]
  $: ready = dataset && samples.length !== 0

  $: if (ready) {
    labels = dataset.labels
    filterOptions = [
      { name: 'Label', label: 'labels', options: labels },
      // TODO: Fetch existing users for options
      { name: 'User', label: 'users', options: [] },
      { name: 'Divided  labels', label: 'divided_labels', options: ['True', 'False'] }
    ]
  }

  onMount(() => {
    filterData()
  })

  async function filterData() {
    samples = []

    // Find filled filter options
    let params = {}
    for (const [key, value] of Object.entries(filterParams)) {
      if (value !== '' && value !== undefined) {
        params[key] = value
      }
    }
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
      .then((response) => {
        samples.push(...response.data)
        // Remove empty entries (caused by backend error) from array
        samples = samples.filter((el) => el != null)
      })
      .catch((err) => console.log(err))
  }

  async function send(sample_id) {
    console.log('SampleID', sample_id)
    const current = samples.find(sample => sample.id = sample_id)
    console.log('New labels:', current.labels)

    // console.log("checked labels:", samples)
    /*
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

     */
  }
</script>

{#if ready}
  <Card>
    <div class="wrapper">
      <div class="menu">
        <ul>
          {#each filterOptions as filterOption, i}
            <Select
              bind:value={filterParams[filterOption.label]}
              emptyFirst={true}
              label={filterOption.name}
              values={filterOption.options}
            />
          {/each}
          <Input bind:value={filterParams['free_text']} type="text" label="Free text" />
        </ul>
        <Button label="Filter" on:click={filterData} />
      </div>
      <div class="mw9 center ph3-ns">
        <div class="cf ph2-ns">
          {#each samples as sample}
            {#if sample}
              <div class="fl w-100 w-third-ns pa2 samples">
                {#if Object.keys(mappings).includes(sample.type)}
                  <div class="reassign">
                    <CheckboxList values="{labels}" bind:checked={sample.labels}>
                    </CheckboxList>
                    <button class="mb3" on:click={send(sample.id)}>
                      <ion-icon class="icon" name="checkmark-circle-outline"></ion-icon>
                    </button>
                  </div>
                  <svelte:component this={mappings[sample.type]} data={sample.content} />
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

    .reassign {
        display: grid;
        grid-template-columns: 2fr 1fr;
    }

    .reassign button {
        background-color: transparent;
        border: none;
    }

    .icon {
        font-size: 25px;
    }
</style>
