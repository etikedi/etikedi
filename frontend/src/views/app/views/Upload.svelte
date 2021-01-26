<script lang="ts">
  import axios from 'axios'

  import File from '../../../ui/File.svelte'
  import Input from '../../../ui/Input.svelte'
  import Button from '../../../ui/Button.svelte'
  import Select from '../../../ui/Select.svelte'
  import { DATASET_TYPES } from '../../../store/datasets'

  let error: null | string = null

  let contents: HTMLInputElement | null = null
  let features: HTMLInputElement | null = null
  const form = {
    name: '',
    sample_type: '',
  }

  async function upload() {
    error = null
    if (contents.files.length !== 1 || features.files.length !== 1) {
      error = 'No files selected'
      return
    }
    const fd = new FormData()
    fd.append('name', form.name)
    fd.append('sample_type', form.sample_type)
    fd.append('features', features.files[0])
    fd.append('contents', contents.files[0])

    const { data } = await axios({
      url: '/datasets',
      method: 'post',
      data: fd,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    console.log(data)
  }
</script>

<h1>Upload</h1>

<form on:submit|preventDefault={upload}>
  <Input label="Name" bind:value={form.name} />
  <Select label="Type" bind:value={form.sample_type} values={DATASET_TYPES} />
  <div class="uploads">
    <File type="file" label="Data" accept="application/zip" bind:element={contents} />
    <File type="file" label="Features" accept="text/comma-separated-values" bind:element={features} />
  </div>
  <Button full label="Upload" type="submit" />
  {#if error}
    <p>{error}</p>
  {/if}
</form>

<style>
  .uploads {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 1em;
  }
</style>
