<script>
  import { Nav } from 'svelte-chota'

  import { auth } from '../store/auth'
</script>

<style>
  div :global(.nav) {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    z-index: 10;
    height: 3em;
    border-bottom: 1px solid black;
    background-color: #fffffff5;
  }

  div {
    margin-bottom: 3em;
  }
</style>

<div>
  <Nav class="nav">
    <a slot="left" class="active" href="/about">About</a>

    <a slot="center" href="/" class="brand">Aergia</a>

    <!-- <a slot="right" href={$auth.token ? '/logout' : '/app'}>
      {#if $auth.token}Logout{:else}Login{/if}
		</a> -->
    <a slot="right" href="/app">App</a>
  </Nav>
</div>
