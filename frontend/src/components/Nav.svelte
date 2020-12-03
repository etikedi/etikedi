<script>
  import { logout, token } from '../store/auth'

  export let segment
</script>

<style>
  div header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    z-index: 10;
    background-color: #009fff;
    padding: 0.5rem 1rem;
    color: white;
  }

  div {
    margin-bottom: 3em;
  }

  h3 {
    margin: 0;
  }

  a {
    color: inherit;
    font-size: 1.15em;
  }
</style>

<div>
  <header class="navbar">
    <section class="navbar-section">
      <a href="/" class="btn btn-link"> Home</a>
      <a href="/about" class="btn btn-link">About</a>
    </section>
    <section class="navbar-center">
      <h3>Aergia</h3>
    </section>
    <section class="navbar-section">
      {#if segment === 'app' && $token}
        <a href="/" on:click={logout} class="btn btn-link">Logout</a>
      {:else}<a href="/app" class="btn btn-link">App</a>{/if}
    </section>
  </header>
</div>
