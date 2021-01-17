<script lang="ts">
  import Card from '../../../ui/Card.svelte'
  import DatasetStats from '../components/DatasetStats.svelte'

  export let dataset
</script>

<Card>
  <h2 class="ma0">{dataset.name}</h2>
  <div class="flex justify-between">
    <DatasetStats statistics={dataset.statistics} />
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

<style>
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
