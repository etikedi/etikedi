<script>
  import { onMount } from 'svelte'
  import axios from 'axios'
  import { router } from 'tinro'

  import Select from '../../../ui/Select.svelte'
  import Button from '../../../ui/Button.svelte'
  import Card from '../../../ui/Card.svelte'
  import Input from '../../../ui/Input.svelte'
  import CheckboxList from '../../../ui/CheckboxList.svelte'
  import Image from '../components/labeling/Image.svelte'
  import Table from '../components/labeling/Table.svelte'

  import { data as datasets } from '../../../store/datasets'
  import { data as users, load } from '../../../store/users'

  const mappings = {
    tables: Table,
    image: Image,
    text: Table,
  }

  const { id } = router.params()
  let dataset, labels, samplesReady, filterOptions, ready
  let samples = []
  let filterParams = { page: 0, limit: 15 }

  $: dataset = $datasets[id]
  $: ready = dataset && $users.length > 0
  $: samplesReady = samples.length !== 0

  $: if (ready) {
    console.log(dataset)
    labels = dataset.labels
    filterOptions = [
      { name: 'Label', label: 'labels', options: labels },
      { name: 'User', label: 'users', options: $users },
      { name: 'Divided  labels', label: 'divided_labels', options: [true, false] },
    ]
  }

  onMount(() => {
    load()
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
        labeled: true,
        ...params,
      },
    })
      .then((response) => {
        samples.push(...response.data)
        // Remove empty entries (caused by backend error) from array
        samples = samples.filter((el) => el != null)
      })
      .catch((err) => console.log(err))
  }

  async function send(sample_id) {
    const current = samples.find((sample) => sample.id === sample_id)
    console.log(current.associations)
    if (current.associations.length > 1) {
      alert(`It's not allowed to reassign more than one label.`)
      return
    }

    await axios({
      method: 'post',
      url: `/samples/${sample_id}`,
      params: {
        label_id: current.associations[0].id,
      },
    })
      .then((res) => {
        // Do something with next sample
      })
      .catch((err) => console.log(err))
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
          <Input bind:value={filterParams['page']} type="text" label="Page number" />
          <Input bind:value={filterParams['limit']} type="text" label="Samples per page" />
        </ul>
        <Button
          label="Filter"
          on:click={() => {
            filterData()
          }}
        />
      </div>
      <div class="samples">
        {#if samplesReady}
          {#each samples as sample}
            {#if sample}
              <div class="sample">
                {#if Object.keys(mappings).includes(sample.type)}
                  <div class="content">
                    <svelte:component this={mappings[sample.type]} data={sample.content} />
                  </div>
                  <div class="reassign">
                    <CheckboxList values={labels} bind:checked={sample.associations} />
                    <button class="mb3" on:click={send(sample.id)}>
                      <ion-icon class="icon" name="checkmark-circle-outline" />
                    </button>
                  </div>
                  <hr />
                {:else}
                  <p>Unsupported type {sample.type}</p>
                {/if}
              </div>
            {/if}
          {/each}
          <div class="page">
            {#if filterParams.page > 0}
              <ion-icon
                class="icon"
                name="arrow-back-outline"
                on:click={() => {
                  filterParams.page = filterParams.page - 1
                  filterData()
                }}
              />
            {/if}
            <Card>Current page: {filterParams.page}</Card>
            <ion-icon
              class="icon"
              name="arrow-forward-outline"
              on:click={() => {
                filterParams.page = filterParams.page + 1
                filterData()
              }}
            />
          </div>
        {/if}
      </div>
    </div>
  </Card>
{/if}

<style>
  .wrapper {
    display: grid;
    grid-template-columns: 1fr 5fr;
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
    padding-left: 15px;
    align-self: center;
    display: grid;
  }

  .sample {
    display: grid;
    justify-self: center;
  }

  .sample hr {
    border: 1px solid grey;
  }

  .reassign {
    margin-top: 30px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
  }

  .reassign button {
    background-color: transparent;
    border: none;
  }

  .icon {
    font-size: 1.75em;
    cursor: pointer;
  }

  .content {
    justify-self: center;
    overflow: auto;
  }

  .page {
    justify-self: center;
    display: flex;
    flex-direction: row;
    align-items: center;
  }
</style>
