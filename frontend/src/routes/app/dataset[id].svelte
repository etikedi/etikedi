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

    let filter = [
        {name: 'User', options: ["Me", "You", "We"]},
        {name: 'Label', options: ["Dog", "Cat", "Mouse"]},
        {name: 'Automatic', options: ["Full Auto", "Semi Auto", "Single Shot"]},
        {name: 'User', options: ["Lisa", "Mona", "Petra"]},
        {name: 'Uncertainty', options: ["Big", "Small"]},
        {name: 'Already checked', options: ["Yes", "No"]},
    ]
</script>

<style>
    .wrapper {
        display: grid;
        grid-template-columns: 1fr 3fr;
        column-gap: 35px;
    }
</style>

<h1>Dataset {id}</h1>
<div class="wrapper">
    <ul class="menu">
        <!-- menu header text -->
        <li class="divider" data-content="FILTER OPTIONS">
        </li>
        <!-- menu item with form control -->
        {#each filter as filterOption}
            <li class="menu-item">
                <!-- form select control -->
                <div class="form-group">
                    <label>{filterOption.name}
                        <select class="form-select">
                            <option disabled selected value style="display: none"></option>
                            {#each filterOption.options as option}
                                <option>{option}</option>
                            {/each}
                        </select>
                    </label>
                </div>
            </li>
        {/each}
        <!-- menu divider -->
        <li class="divider"></li>
        <!-- menu item with badge -->
        <li class="menu-item">
            <button class="btn btn-lg">
                Save
            </button>
        </li>
    </ul>
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
</div>
