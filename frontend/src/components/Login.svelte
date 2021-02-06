<script lang="ts">
  import { notifier } from '@beyonk/svelte-notifications'

  import Input from '../ui/Input.svelte'
  import Button from '../ui/Button.svelte'

  import type { LoginForm } from '../store/auth'
  import { login } from '../store/auth'

  let loading = false
  let form: LoginForm = {
    username: '',
    password: '',
  }

  async function submit() {
    try {
      loading = true
      if (!form.username || !form.password) {
        notifier.danger('Input missing')
        return
      }
      await login(form)
      notifier.success('Logged in 🔐')
    } catch (e) {
      form.password = ''
      notifier.danger(e.response.data.detail)
    } finally {
      loading = false
    }
  }
</script>

<form on:submit|preventDefault={submit}>
  <Input bind:value={form.username} disabled={loading} label="Username" />
  <Input bind:value={form.password} disabled={loading} label="Password" type="password" />

  <Button type="submit" disabled={loading} {loading} label="Login" icon="person-circle-sharp" />
</form>

<style>
  form {
    margin: 4em auto;
    max-width: 20em;
  }
</style>
