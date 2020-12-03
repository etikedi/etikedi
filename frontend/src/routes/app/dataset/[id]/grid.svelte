<script context="module">
    export function preload(page) {
        return {id: page.params.id}
    }
</script>
<script>
    export let id

    let mock = [
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Lisa", label: "Dog"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Mona", label: "Dog"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Petra", label: "Cat"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Lisa", label: "Cat"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Lisa", label: "Cat"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Lisa", label: "Mouse"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Petra", label: "Cat"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Petra", label: "Mouse"},
        {sampleId: "524", content: "dmaklwdmkwalmdkl", user: "Mona", label: "Cat"},
    ]

    let displayed = mock

    let filter = [
        {name: 'User', label: 'user', options: ["Lisa", "Mona", "Petra"]},
        {name: 'Label', label: 'label', options: ["Dog", "Cat", "Mouse"]},
        {name: 'Automatic', label: 'automatic', options: ["Full Auto", "Semi Auto", "Single Shot"]},
        {name: 'Uncertainty', label: 'uncertainty', options: ["Big", "Small"]},
        {name: 'Already checked', label: 'checked', options: ["Yes", "No"]},
    ]

    let inputs = []

    function filterData() {
        let array = []
        inputs.forEach(input => {
            if (input.value) {
                array.push(mock.filter(sample => sample[input.name] === input.value))
            }
        })
        array = array.flat()
        // Eliminate duplicates and convert it back to array
        displayed = [...new Set([...array])]
    }
</script>

<style>
    .position {
        position: fixed;
        left: 3em;
        margin-right: 3em;
    }

    .wrapper {
        display: grid;
        grid-template-columns: 1fr 4fr;
        column-gap: 35px;
    }
</style>


<div class="position">
    <h1>Dataset {id}</h1>
    <div class="wrapper">
        <ul class="menu">
            <!-- menu header text -->
            <li class="divider" data-content="FILTER OPTIONS">
            </li>
            <!-- menu item with form control -->
            {#each filter as filterOption, i}
                <li class="menu-item">
                    <!-- form select control -->
                    <div class="form-group">
                        <label>{filterOption.name}
                            <select bind:this={inputs[i]} name="{filterOption.label}" class="form-select">
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
                <button class="btn btn-lg" on:click={filterData}>
                    Save
                </button>
            </li>
        </ul>
        <div class="container">
            <div class="columns">
                {#each displayed as sample}
                    <div class="column col-4 card mb-2">
                        <div class="card-title text-gray">Sample {sample.sampleId}</div>
                        <div class="card-body">
                            {sample.content}
                            {sample.user}
                            {sample.label}
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    </div>
</div>
