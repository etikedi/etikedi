<script lang="ts">
  import Input from '../ui/Input.svelte'
  import Button from '../ui/Button.svelte'

  import type { LoginForm } from '../store/auth'
  import { login } from '../store/auth'

  let loading = false
  let error = ''
  let form: LoginForm = {
    // TODO: Eventually remove
    username: 'ernst_haft',
    password: 'adminadmin',
  }

  async function submit() {
    try {
      loading = true
      error = ''
      await login(form)
    } catch {
      error = 'Nope'
      form.password = ''
    } finally {
      loading = false
    }
  }
</script>

<style>
  form {
    margin: 4em auto;
    max-width: 20em;
  }
</style>

<form on:submit|preventDefault={submit}>
  <Input bind:value={form.username} disabled={loading} label="Username" />
  <Input bind:value={form.password} disabled={loading} label="Password" type="password" />

  <Button type="submit" disabled={loading} {loading} label="Login" icon="person-circle-sharp" />

  {#if error}
    <p class="text-error">{error}</p>
  {/if}
</form>
