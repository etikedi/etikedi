<script>
  import Login from '../../components/Login.svelte'

  import { auth } from '../../store/auth'
</script>

<div>{$auth.token}</div>
{#if $auth.token !== null}
  {#if $auth.token}
    <slot />
  {:else}
    <Login />
  {/if}
{/if}
