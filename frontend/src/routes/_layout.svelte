<script>
  import { onMount } from 'svelte'
  import 'chota/dist/chota.min.css'

  import Login from '../components/Login.svelte'

  import { auth, login } from '../store/auth'

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

{#if $auth.token !== null}
  <main>
    {#if $auth.token}
      <slot />
    {:else}
      <Login />
    {/if}
  </main>
{/if}
