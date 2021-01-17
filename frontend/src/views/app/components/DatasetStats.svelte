<script lang="ts">
  import { humanize } from '../../../lib/human'

  export let statistics
</script>

<div class="flex items-center">
  <table>
    <tr>
      <td>Total</td>
      <td class="value">{humanize(statistics.total_samples)}</td>
      <td>Features</td>
      <td class="value">{humanize(statistics.features)}</td>
    </tr>
    <tr>
      <td>Labeled</td>
      <td class="value">{humanize(statistics.labelled_samples)}</td>
      <td>Labels</td>
      <td class="value">{humanize(statistics.labels)}</td>
    </tr>
  </table>
  <div class="percentage">
    {Math.round((statistics.labelled_samples / statistics.total_samples) * 100)}%
  </div>
</div>

<style>
  td.value {
    padding-left: 1em;
    padding-right: 2em;
    font-family: monospace;
    font-weight: bold;
  }

  .percentage {
    font-family: monospace;
    font-weight: bold;
    font-size: 2em;
  }
</style>
