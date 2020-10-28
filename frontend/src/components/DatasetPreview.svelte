<script>
    export let dataset

    function kFormatter(num) {
        return Math.abs(num) > 999 ? Math.sign(num)*((Math.abs(num)/1000).toFixed(1)) + 'k' : Math.sign(num)*Math.abs(num)
    }
</script>

<style>
    .card {
        border: 2px solid #DEF1F7;
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
            <div class="card-subtitle text-gray">icons</div>
        </div>
        <div class="col-2 pl-2">
            <div>Total</div>
            <div>Labeled</div>
        </div>
        <div class="col-1">
            <div>{kFormatter(dataset.size)}</div>
            <div>{kFormatter(dataset.labeled)}</div>
        </div>
        <div class="col-2 pl-2">
            <div>Features</div>
            <div>Labels</div>
        </div>
        <div class="col-1">
            <div>{dataset.features}</div>
            <div>{dataset.labels}</div>
        </div>
        <div class="col-2 h2">{Math.round(dataset.labeled / dataset.size * 100)}%</div>
        <div class="col-1 button">
            <a href="app/dataset{dataset.id}">
                <i class="icon icon-2x icon-arrow-right"></i>
            </a>
        </div>
    </div>
</div>