<script lang="ts">
  export let values: any
  export let label: string = ''
  export let selected = []

  let items

  $: console.log(values)

  function dropList() {
    if (items.classList.contains('visible')) {
      items.classList.remove('visible')
      items.style.display = 'none'
    } else {
      items.classList.add('visible')
      items.style.display = 'block'
    }
  }

</script>

<style>
    .dropdown-check-list {
        display: inline-block;
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
        padding: 2px;
        display: none;
        margin: 0;
        border: 1px solid #ccc;
        border-top: none;
    }

    .dropdown-check-list ul.items li {
        list-style: none;
    }

</style>

<div on:click={dropList} class="mb3 dropdown-check-list">
  <span class="anchor">Select Fruits</span>
  <ul bind:this={items} class="items">
    {#each values as v, i}
      <li>
        <input type="checkbox" bind:checked={values[i].checked}>
        {v.name}
      </li>
    {/each}
  </ul>
</div>
