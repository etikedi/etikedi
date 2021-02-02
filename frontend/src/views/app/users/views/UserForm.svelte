<script lang="ts">
  import { onMount } from 'svelte'
  import { router } from 'tinro'
  import { notifier } from '@beyonk/svelte-notifications'
  import copy from 'copy-to-clipboard'

  import Button from '../../../../ui/Button.svelte'
  import Input from '../../../../ui/Input.svelte'
  import Checkbox from '../../../../ui/Checkbox.svelte'
  import Select from '../../../../ui/Select.svelte'

  import type { User, UserWithoutID } from '../../../../store/users'
  import { data, loading, load, empty, add, update, generateNewPassword } from '../../../../store/users'

  const { id } = router.params()
  const edit = id !== 'new'

  let user: UserWithoutID | null = null

  $: if (!user) {
    if (edit) {
      const tmp = parseInt(id)
      user = $data.find((user) => user.id === tmp)
    } else {
      user = empty()
    }
  }

  function showAndCopyPassword(password: string) {
    notifier.info(`New password copied to clipboard: ${password}`, 60_000)
    copy(password)
  }

  async function submit() {
    try {
      if (edit) {
        await update(id, user)
      } else {
        const password = await add(user)
        showAndCopyPassword(password)
      }
      notifier.success('Saved')
      back()
    } catch (e) {
      console.error(e)
      notifier.error(e)
    }
  }

  async function gen() {
    const password = await generateNewPassword(id)
    console.log(password)
    showAndCopyPassword(password)
  }

  function back() {
    router.goto('./')
  }

  onMount(() => {
    load()
  })
</script>

<div>
  <Button icon="arrow-back-circle-sharp" label="Back" on:click={back} />
  <br />
  {#if $loading === false && user !== null}
    <h2>User</h2>
    <form on:submit|preventDefault={submit}>
      <Input bind:value={user.fullname} label="Full Name" />
      <Input bind:value={user.username} label="Username" />
      <Input bind:value={user.email} label="E-Mail" />
      <Select bind:value={user.roles} label="Role" values={['worker', 'admin']} />
      <Checkbox bind:value={user.is_active} label="Active" />

      <Button type="submit" label={edit ? 'Update' : 'Create'} icon="checkmark-circle-sharp" />
    </form>
    {#if edit}
      <hr />
      <Button type="button" label="Regenerate Password" icon="refresh-circle-sharp" on:click={gen} />
    {/if}
  {:else}
    <div class="loading loading-lg" />
  {/if}
</div>
