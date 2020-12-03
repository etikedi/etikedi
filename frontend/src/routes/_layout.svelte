<script>
  import { onMount } from 'svelte'
  import 'spectre.css/dist/spectre.css'

  import Nav from '../components/Nav.svelte'
  import { login } from '../store/auth'

  export let segment

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

<Nav {segment} />
<main>
  <slot />
</main>
