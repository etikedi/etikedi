<script lang="ts">
  import { sanitize } from 'dompurify'

  const config = { USE_PROFILES: { html: true }, FORBID_ATTR: ['href', 'src'] }

  export let data = null
  export let toDecode = true
  let decoded

  $: decoded = toDecode? window.atob(data) : data
  $: sanitized = sanitize(decoded, config)
</script>

{#if data}
  {@html sanitized}
{/if}
