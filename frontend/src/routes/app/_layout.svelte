<script>
  import Login from '../../components/Login.svelte'

  import { auth } from '../../store'

  const { token } = auth
</script>

{#if $token !== null}
  {#if $token}
    <slot />
  {:else}
    <Login />
  {/if}
{/if}
