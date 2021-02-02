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
        <ion-icon class="settings" name="cog-sharp" />
      </a>
      <a href="app/dataset/{dataset.id}/graphs">
        <ion-icon name="analytics-sharp" />
      </a>
      <a href="app/dataset/{dataset.id}/labeled">
        <ion-icon class="labeled" name="grid-sharp" />
      </a>
      <a href="app/dataset/{dataset.id}/label">
        <ion-icon class="play" name="play-circle-sharp" />
      </a>
    </div>
  </div>
</Card>

<style>
  .actions > a {
    margin-left: 1.25rem;
  }

  ion-icon {
    font-size: 1.5rem;
  }

  ion-icon.play {
    font-size: 3rem;
    color: var(--clr-primary);
  }
</style>
