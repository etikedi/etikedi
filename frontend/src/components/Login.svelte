<script>
  import { auth } from '../store'

  let loading = false
  let error = ''
  let form = {
    username: 'ernst_haft',
    password: 'adminadmin',
  }

  async function submit() {
    try {
      loading = true
      error = ''
      await auth.login(form)
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
  <div class="form-group">
    <label class="form-label">
      Name
      <input class="form-input" type="text" bind:value={form.username} disabled={loading} />
    </label>
  </div>

  <div class="form-group">
    <label class="form-label">
      Password
      <input class="form-input" type="password" bind:value={form.password} disabled={loading} />
    </label>
  </div>

  <button type="submit" class="btn btn-primary" disabled={loading} class:loading>Login</button>

  {#if error}
    <p class="text-error">{error}</p>
  {/if}
</form>
