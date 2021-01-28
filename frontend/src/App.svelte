<script lang="ts">
  import { onMount } from 'svelte'
  import { Route } from 'tinro'
  import { NotificationDisplay } from '@beyonk/svelte-notifications'

  import Home from './views/Home.svelte'
  import About from './views/About.svelte'
  import Nav from './components/Nav.svelte'

  import { login } from './store/auth'
  import AppWrapper from './views/app/App.svelte'

  onMount(() => {
    login()
  })
</script>

<Nav />
<main>
  <Route path="/">
    <Home />
  </Route>
  <Route path="/about">
    <About />
  </Route>
  <Route path="/app/*">
    <AppWrapper />
  </Route>
  <NotificationDisplay />
</main>

<style>
  main {
    position: relative;
    max-width: 56em;
    padding: 2em;
    margin: 0 auto;
    box-sizing: border-box;
  }
</style>
