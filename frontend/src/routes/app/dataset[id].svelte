<script context="module">
    export function preload(page) {
        return {id: page.params.id}
    }
</script>
<script>
    export let id

    let mock = [
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl"},
    ]
</script>

<h1>Dataset {id}</h1>
<div class="container">
    <div class="columns">
        {#each mock as sample}
            <div class="column col-4 card mb-2">
                <div class="card-title text-gray">Sample {sample.sampleId}</div>
                <div class="card-body">{sample.content}</div>
            </div>
        {/each}
    </div>
</div>