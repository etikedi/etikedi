<script>
  import { Input, Field, Button } from 'svelte-chota'

  import { login } from '../store/auth'

  let loading = false
  let error = ''
  let form = {
    username: '',
    password: '',
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

<form on:submit|preventDefault={submit}>
  <Field label="Username">
    <Input type="text" bind:value={form.username} disabled={loading} />
  </Field>
  <Field label="Password">
    <Input type="password" bind:value={form.password} disabled={loading} />
  </Field>

  <Button submit primary {loading}>Login</Button>

  {#if error}
    <p class="text-error">{error}</p>
  {/if}
</form>
