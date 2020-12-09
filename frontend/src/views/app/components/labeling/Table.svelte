<script lang="ts">
  import { sanitize } from 'dompurify'

  const config = { USE_PROFILES: { html: true }, FORBID_ATTR: ['href', 'src'] }

  export let data = null

  $: decoded = window.atob(data)
  $: sanitized = sanitize(decoded, config)
</script>

{#if data}
  {@html sanitized}
{/if}
