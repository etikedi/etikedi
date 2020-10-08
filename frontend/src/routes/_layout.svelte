<script>
  import { onMount } from 'svelte'
  import 'chota/dist/chota.min.css'

  import Nav from '../components/Nav.svelte'
  import { login } from '../store/auth'

  onMount(async () => {
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
  <slot />
</main>
