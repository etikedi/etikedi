<script lang="ts">
  export let values: any
  export let selected = []
  export let checked

  let items
  selected = values

  // Delete eventually set checked
  values = values.map(label => {
    delete label.checked
    return label
  })

  // Set initial checked
  values.forEach(label => {
    checked.forEach(current => {
      if (label.id === current.id) {
        label.checked = true
      }
    })
  })

  function dropList() {
    if (items.classList.contains('visible')) {
      items.classList.remove('visible')
      items.style.display = 'none'
    } else {
      items.classList.add('visible')
      items.style.display = 'grid'
    }
  }

</script>

<style>
    .anchor {
        height: 25px;
    }

    .dropdown-check-list {
        display: inline-block;
        position: relative;
    }

    .dropdown-check-list .anchor {
        position: relative;
        cursor: pointer;
        display: inline-block;
        padding: 5px 50px 5px 10px;
        border: 1px solid #ccc;
    }

    .dropdown-check-list .anchor:after {
        position: absolute;
        content: "";
        border-left: 2px solid black;
        border-top: 2px solid black;
        padding: 5px;
        right: 10px;
        top: 20%;
        -moz-transform: rotate(-135deg);
        -ms-transform: rotate(-135deg);
        -o-transform: rotate(-135deg);
        -webkit-transform: rotate(-135deg);
        transform: rotate(-135deg);
    }

    .dropdown-check-list .anchor:active:after {
        right: 8px;
        top: 21%;
    }

    .dropdown-check-list ul.items {
        width: 100%;
        position: absolute;
        background-color: white;
        z-index: 1000;
        padding: 2px;
        display: none;
        margin: -1px 0 0 0;
        border: 1px solid #ccc;
    }

    .dropdown-check-list ul.items li {
        list-style: none;
        overflow: auto;
    }

    .dropdown-check-list ul.items li input {
        overflow: auto;
    }

</style>

<div class="mb3 dropdown-check-list">
  <span on:click={dropList} class="anchor">Reassign label...</span>
  <ul bind:this={items} class="items">
    {#each values as v, i}
      <li>
        <input type="checkbox" bind:checked={values[i].checked}
               on:change={() => {checked = values.filter(label => label.checked === true)}}>
        {v.name}
      </li>
    {/each}
  </ul>
</div>