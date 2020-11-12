<script>
    import {onMount} from 'svelte'

    import DatasetPreview from '../../components/DatasetPreview.svelte'
    import {datasets} from '../../store'

    const {data, load} = datasets

    let mock = [
        {
            id: 1,
            name: "CIFAR-10",
            type: "label",
            size: 10000,
            labeled: 5600,
            features: 31,
            labels: 10
        }, {
            id: 2,
            name: "Servo",
            type: "select",
            size: 12000,
            labeled: 431,
            features: 18,
            labels: 6
        }, {
            id: 3,
            name: "DWTC",
            type: "annotate",
            size: 7400,
            labeled: 6032,
            features: 15,
            labels: 18
        }, {
            id: 4,
            name: "HTML Collection",
            type: "annotate",
            size: 3250,
            labeled: 5600,
            features: 9,
            labels: 3
        }
    ]

    onMount(() => {
        load()
    })
</script>

<style>
    .header {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1em;
    }

    h1 {
        margin: 0;
    }
</style>

<div class="header">
    <h1>Datasets</h1>
    <a href="/app/upload">
        <button class="btn btn-lg">
            Add one
        </button>
    </a>
</div>

{#each mock as dataset}
    <DatasetPreview {dataset}/>
{/each}
