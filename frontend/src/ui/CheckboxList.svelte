<script lang="ts">
  import { onMount } from 'svelte'

  export let values: any
  export let checked

  let labels, items

  // Remove probably set checked value
  labels = values.map(label => {
    return { name: label.name, id: label.id }
  })

  // Set checked labels
  checked.forEach(check => {
    labels.find(sample => sample.id === check.id).checked = true
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
        border-radius: var(--round);
        border: 2px solid var(--clr-primary-light);
    }

    .dropdown-check-list ion-icon {
        position: absolute;
        right: 10px;
        top: 5px;
        font-size: 1.75em;
        color: var(--clr-primary-light);
        cursor: pointer;
    }

    .dropdown-check-list ul.items {
        width: 100%;
        position: absolute;
        background-color: white;
        z-index: 1000;
        padding: 2px;
        display: none;
        margin: -1px 0 0 0;
        border-radius: var(--round);
        border: 2px solid var(--clr-primary-light);
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
  <ion-icon on:click={dropList} name="caret-down-circle-sharp" />
  <ul bind:this={items} class="items">
    {#each values as v, i}
      <li>
        <input type="checkbox" bind:checked={labels[i].checked}
               on:change={() => {checked = labels.filter(label => label.checked === true)}}>
        {v.name}
      </li>
    {/each}
  </ul>
</div>