<script lang="ts">
  import { onMount } from 'svelte'
  import { Route } from 'tinro'
  import { NotificationDisplay } from '@beyonk/svelte-notifications'
  import { Modal } from 'svelte-simple-modal'

  import Home from './views/Home.svelte'
  import About from './views/About.svelte'
  import Nav from './components/Nav.svelte'

  import { login } from './store/auth'
  import AppWrapper from './views/app/App.svelte'

  onMount(() => {
    login()
  })
</script>

<Modal>
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
</Modal>

<style>
  main {
    position: relative;
    padding: 3em 6em;
    margin: 0 auto;
    box-sizing: border-box;
  }
</style>
