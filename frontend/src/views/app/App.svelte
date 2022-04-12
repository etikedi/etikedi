<script lang="ts">
  import { Route } from 'tinro'
  import Login from '../../components/Login.svelte'
  import { token } from '../../store/auth'
  import { load } from '../../store/datasets'
  import { load as loadMe } from '../../store/me'
  import Result from './components/battle/Result.svelte'
  import Config from './components/Config.svelte'
  import Nav from './components/Nav.svelte'
  import Me from './users/Me.svelte'
  import Users from './users/Users.svelte'
  import Battle from './views/battle/Battle.svelte'
  import BattleDashboard from './views/battle/Dashboard.svelte'
  import Dashboard from './views/Dashboard.svelte'
  import Graphs from './views/Graphs.svelte'
  import Label from './views/Label.svelte'
  import LabeledGrid from './views/LabeledGrid.svelte'
  import LabelingFunctions from './views/LabelingFunctions.svelte'
  import Upload from './views/Upload.svelte'

  $: if ($token) {
    load()
    loadMe()
  }
</script>

{#if $token !== null}
  {#if $token}
    <!-- NAV -->
    <Nav />
    <hr />

    <!-- USERS -->
    <Route path="/me">
      <Me />
    </Route>
    <Route path="/users/*">
      <Users />
    </Route>

    <!-- DATASETS -->
    <Route path="/upload">
      <Upload />
    </Route>
    <Route path="/dataset/:id/*">
      <Route path="/labelingfunctions">
        <LabelingFunctions />
      </Route>
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
      <Route path="/battle/*">
        <Route path="/dashboard">
          <BattleDashboard />
        </Route>
        <Route path="/new">
          <Battle />
        </Route>
        <Route path="/result">
          <Result />
        </Route>
      </Route>
    </Route>

    <!-- DASHBOARD -->
    <Route path="/">
      <Dashboard />
    </Route>
  {:else}
    <Login />
  {/if}
{/if}
