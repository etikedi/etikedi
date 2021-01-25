<script lang="ts">
  import { sanitize } from 'dompurify'

  export let data = null
  export let toDecode = true
  let decoded

  $: decoded = toDecode ? window.atob(data) : data
  $: cleaned = decoded.indexOf('<tbody>') === -1 ? decoded : `<table>${decoded}</table>` // See -> https://github.com/cure53/DOMPurify/issues/324#issuecomment-469689764
  $: sanitized = sanitize(cleaned)
</script>

{#if data}
  {@html sanitized}
{/if}
