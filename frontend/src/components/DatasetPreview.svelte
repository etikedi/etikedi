<script>
  import { toHumanString } from 'human-readable-numbers'

  export let dataset
</script>

<style>
  .card {
    border: 2px solid #def1f7;
    border-radius: 15px;
  }

  .button {
    align-self: center;
    /* cursor: pointer; */
  }
</style>

<div class="card mb-2 container">
  <div class="card-body columns">
    <div class="col-3">
      <div class="card-title h5">{dataset.name}</div>
      <div class="card-subtitle text-gray">ID: {dataset.id}</div>
    </div>
    <div class="col-2 pl-2">
      <div>Total</div>
      <div>Labeled</div>
    </div>
    <div class="col-1">
      <div>{toHumanString(dataset.size || 0)}</div>
      <div>{toHumanString(dataset.labeled || 0)}</div>
    </div>
    <div class="col-2 pl-2">
      <div>Features</div>
      <div>Labels</div>
    </div>
    <div class="col-1">
      <div>{dataset.features || 0}</div>
      <div>{dataset.labels.length}</div>
    </div>
    <div class="col-2 h2">{Math.round((dataset.labeled / dataset.size) * 100)}%</div>
    <div class="col-1 button">
      <a href="app/dataset/{dataset.id}/label"> <i class="icon icon-2x icon-arrow-right" /> </a>
    </div>
  </div>
</div>
