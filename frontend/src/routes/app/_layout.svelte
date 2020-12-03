<script>
  import Login from '../../components/Login.svelte'

  import { token } from '../../store/auth'
  import { load } from '../../store/datasets'

  $: if ($token) {
    load()
  }
</script>

{#if $token !== null}
  {#if $token}
    <slot />
  {:else}
    <Login />
  {/if}
{/if}
