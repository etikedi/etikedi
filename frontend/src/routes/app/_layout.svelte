<script>
  import Login from '../../components/Login.svelte'

  import { token } from '../../store/auth'
</script>

{#if $token !== null}
  {#if $token}
    <slot />
  {:else}
    <Login />
  {/if}
{/if}
