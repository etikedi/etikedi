<script lang="ts">
  import { Route } from 'tinro'

  import Login from '../../components/Login.svelte'

  import { token } from '../../store/auth'
  import { load } from '../../store/datasets'

  import Dashboard from './views/Dashboard.svelte'
  import Config from './views/Config.svelte'
  import Label from './views/Label.svelte'
  import Upload from './views/Upload.svelte'

  $: if ($token) {
    load()
  }
</script>

{#if $token !== null}
  {#if $token}
    <Route path="/upload">
      <Upload />
    </Route>
    <Route path="/">
      <Dashboard />
    </Route>
    <Route path="/dataset/:id/*">
      <Route path="/config">
        <Config />
      </Route>
      <Route path="/label">
        <Label />
      </Route>
    </Route>
  {:else}
    <Login />
  {/if}
{/if}
