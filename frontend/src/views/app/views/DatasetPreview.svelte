<script lang="ts">
  import type { Dataset } from '../../../store/datasets'
  import { isAdmin } from '../../../store/me'
  import Card from '../../../ui/Card.svelte'
  import DatasetStats from '../components/DatasetStats.svelte'

  export let dataset: Dataset
</script>

<Card>
  <h2 class="ma0">{dataset.name}</h2>
  <div class="flex justify-between">
    <DatasetStats statistics={dataset.statistics} />
    <div class="actions flex items-center">
      {#if $isAdmin}
        <a href="./dataset/{dataset.id}/config">
          <ion-icon class="settings" name="cog-sharp" />
        </a>
      {/if}
      <a href="./dataset/{dataset.id}/labelingfunctions">
        <ion-icon class="functions" name="code" />
      </a>
      <a href="./dataset/{dataset.id}/graphs">
        <ion-icon name="analytics-sharp" />
      </a>
      <a href="./dataset/{dataset.id}/battle/dashboard">
        <ion-icon name="git-compare-outline" />
      </a>
      {#if $isAdmin}
        <a href="./dataset/{dataset.id}/labeled">
          <ion-icon class="labeled" name="grid-sharp" />
        </a>
      {/if}
      <a href="./dataset/{dataset.id}/label">
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
