<script lang="ts">
  import {Route} from 'tinro'

  import Login from '../../components/Login.svelte'

  import {token} from '../../store/auth'
  import {load} from '../../store/datasets'
  import {load as loadMe} from '../../store/me'

  import Dashboard from './views/Dashboard.svelte'
  import Config from './views/Config.svelte'
  import Label from './views/Label.svelte'
  import Upload from './views/Upload.svelte'
  import LabeledGrid from './views/LabeledGrid.svelte'
  import Graphs from './views/Graphs.svelte'
  import Users from './users/Users.svelte'
  import Nav from './components/Nav.svelte'
  import Me from './users/Me.svelte'
  import ALWar from './views/ALWar.svelte'
  import LabelingFunctions from "./views/LabelingFunctions.svelte";

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
        <LabelingFunctions/>
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
      <Route path="/al-war">
        <ALWar />
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
