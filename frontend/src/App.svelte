<script lang="ts">
  import { onMount } from 'svelte'
  import { Route } from 'tinro'

  import Home from './views/Home.svelte'
  import About from './views/about.svelte'
  import Nav from './components/Nav.svelte'

  import { login } from './store/auth'
  import AppWrapper from './views/app/App.svelte'

  onMount(() => {
    login()
  })
</script>

<style>
  main {
    position: relative;
    max-width: 56em;
    background-color: white;
    padding: 2em;
    margin: 0 auto;
    box-sizing: border-box;
  }
</style>

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
</main>
