<script lang="ts">
  import { router } from 'tinro'
  import { logout, token } from '../store/auth'
</script>

<style>
  nav {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    z-index: 10;
    background-color: var(--clr-primary);
    padding: 0.5rem 1rem;
    color: var(--clr-white);
  }

  nav > div {
    flex: 1;
  }

  a {
    font-size: 1.15em;
    border-bottom: 0.1em solid transparent;
    padding: 0.25em 0.5em;
  }
  a:hover:not(.logo) {
    border-bottom: 0.1em solid var(--clr-white);
  }

  .logo {
    font-size: 2.5em;
    font-weight: lighter;
    transform: translateY(-0.1em);
    display: block;
    padding: 0;
  }
</style>

<div class="h3" />
<nav class="flex h3 items-center justify-center">
  <div><a href="/"> Home</a> <a href="/about">About</a></div>
  <div class="tc"><a href="/app" class="logo"> Aergia </a></div>
  <div class="tr">
    {#if $router.path.startsWith('/app') && $token}
      <a href="/" on:click={logout}>Logout</a>
    {:else}<a href="/app">App</a>{/if}
  </div>
</nav>
