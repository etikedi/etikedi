<script lang="ts">
  import { onMount } from 'svelte'
  import { notifier } from '@beyonk/svelte-notifications'

  import type { User } from '../../../store/users'
  import { data, load, changePassword } from '../../../store/me'

  import Button from '../../../ui/Button.svelte'
  import Input from '../../../ui/Input.svelte'

  let user: null | User = null
  let password = ''

  async function submit() {
    try {
      await changePassword(password)
      password = ''
      notifier.success('Password changed')
    } catch (e) {
      notifier.danger(`Error ${e?.response?.data?.detail}`)
    }
  }

  onMount(async () => {
    await load()
    user = $data
  })
</script>

{#if user}
  <h2>{user.fullname}</h2>
  <form on:submit|preventDefault={submit}>
    <Input bind:value={password} label="New password" type="password" />
    <Button type="submit" label="Change password" icon="checkmark-circle-sharp" />
  </form>
{/if}
