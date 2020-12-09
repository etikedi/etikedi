<script>
  import { defaults } from 'sanitize-html'
  // const sanitizeHtml = require('sanitize-html')

  const options = {
    allowedTags: ['table', 'tr', 'td', 'th', 'thead', 'tbody', 'b', 'i', 'em', 'strong'],
  }

  export let data = null

  // $: sanitized = sanitize(data, options)
  console.log(defaults('test'))
</script>

{#if data}
  {@html data}
{/if}
