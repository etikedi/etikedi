<script lang="ts">
  import { Route, router } from 'tinro'

  import Login from '../../components/Login.svelte'

  import { token } from '../../store/auth'
  import { load } from '../../store/datasets'
  import { load as loadMe, isAdmin } from '../../store/me'

  import Dashboard from './views/Dashboard.svelte'
  import Config from './views/Config.svelte'
  import Label from './views/Label.svelte'
  import Upload from './views/Upload.svelte'
  import LabeledGrid from './views/LabeledGrid.svelte'
  import Graphs from './views/Graphs.svelte'
  import Users from './users/Users.svelte'
  import Nav from './components/Nav.svelte'
  import Me from './users/Me.svelte'

  $: if ($token) {
    load()
    loadMe()
  }
</script>

{#if $token !== null}
  {#if $token}
    <Nav />
    <hr />

    <Route path="/upload">
      <Upload />
    </Route>
    <Route path="/dataset/:id/*">
      <Route path="/config">
        <Config />
      </Route>
      <Route path="/label">
        <Label />
      </Route>
      <Route path="/labeled">
        <LabeledGrid />
      </Route>
      <Route path="/graphs">
        <Graphs />
      </Route>
    </Route>
    <Route path="/me">
      <Me />
    </Route>
    <Route path="/users/*">
      <Users />
    </Route>
    <Route path="/">
      <Dashboard />
    </Route>
    <!-- <Route path="/app/*">
      {router.goto($router.path.replace('/app', ''))}
    </Route> -->
  {:else}
    <Login />
  {/if}
{/if}
