<script lang="ts">
  import { isAdmin } from '../../../store/me'
  import Button from '../../../ui/Button.svelte'
</script>

<nav>
  <a href="/app/">
    <Button label="Datasets" icon="albums-sharp" />
  </a>
  <a href="/app/me">
    <Button label="Account" icon="person-circle-sharp" />
  </a>
  {#if $isAdmin}
    <a href="/app/users/">
      <Button label="User management" icon="people-circle-sharp" />
    </a>
  {/if}
</nav>
