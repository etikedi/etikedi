<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'
  import { router } from 'tinro'

  import File from '../../../ui/File.svelte'
  import Input from '../../../ui/Input.svelte'
  import Button from '../../../ui/Button.svelte'
  import Select from '../../../ui/Select.svelte'

  import { create, DATASET_TYPES, loading } from '../../../store/datasets'

  let contents: HTMLInputElement | null = null
  let features: HTMLInputElement | null = null
  const form = {
    name: '',
    sample_type: DATASET_TYPES[0],
  }

  async function upload() {
    try {
      if (contents.files.length !== 1 || features.files.length !== 1) {
        notifier.danger('No files selected')
        return
      }
      const fd = new FormData()
      fd.append('name', form.name)
      fd.append('sample_type', form.sample_type)
      fd.append('features', features.files[0])
      fd.append('contents', contents.files[0])

      await create(fd)
      notifier.success('Uploaded')
      router.goto('./')
    } catch (e) {
      console.error(e)
      notifier.danger(e)
    }
  }
</script>

<h1>Upload</h1>

<form on:submit|preventDefault={upload}>
  <Input label="Name" bind:value={form.name} disabled={$loading} />
  <Select label="Type" bind:value={form.sample_type} values={DATASET_TYPES} disabled={$loading} />
  <div class="uploads">
    <File type="file" label="Data" accept="application/zip" bind:element={contents} disabled={$loading} />
    <File
      type="file"
      label="Features"
      accept="text/comma-separated-values"
      bind:element={features}
      disabled={$loading}
    />
  </div>
  <Button full label="Upload" type="submit" disabled={$loading} />
</form>

<style>
  .uploads {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 1em;
  }
</style>
