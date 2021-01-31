<script lang="ts">
  import { sanitize } from 'dompurify'

  export let data = null

  $: cleaned = data.indexOf('<tbody>') === -1 ? data : `<table>${data}</table>` // See -> https://github.com/cure53/DOMPurify/issues/324#issuecomment-469689764
  $: sanitized = sanitize(cleaned)
</script>

{#if data}
  {@html sanitized}
{/if}
