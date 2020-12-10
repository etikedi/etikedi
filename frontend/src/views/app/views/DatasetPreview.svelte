<script lang="ts">
  import { humanize } from '../../../lib/human'

  import Card from '../../../ui/Card.svelte'

  export let dataset
</script>

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

  .actions > a {
    margin-left: 1em;
  }

  ion-icon.settings {
    font-size: 1.5em;
    /* transform: translateX(0.25em); */
  }

  ion-icon.play {
    font-size: 2.5em;
    color: var(--clr-primary);
  }
</style>

<Card>
  <h2 class="ma0">{dataset.name}</h2>
  <div class="flex justify-between">
    <div class="flex items-center">
      <table>
        <tr>
          <td>Total</td>
          <td class="value">{humanize(dataset.size || 0)}</td>
          <td>Features</td>
          <td class="value">{dataset.features || 0}</td>
        </tr>
        <tr>
          <td>Labeled</td>
          <td class="value">{humanize(dataset.labeled || 0)}</td>
          <td>Labels</td>
          <td class="value">{dataset.labels.length}</td>
        </tr>
      </table>
      <div class="percentage">{Math.round((dataset.labeled / dataset.size) * 100)}%</div>
    </div>
    <div class="actions flex items-center">
      <a href="app/dataset/{dataset.id}/config">
        <ion-icon class="settings" name="cog-outline" />
      </a>
      <a href="app/dataset/{dataset.id}/label">
        <ion-icon class="play" name="play-circle-sharp" />
      </a>
    </div>
  </div>
</Card>
