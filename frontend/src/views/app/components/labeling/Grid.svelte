<script>
  import { onMount } from 'svelte'

  export let displayed = [
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Dog' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Mona', label: 'Dog' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Petra', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Lisa', label: 'Mouse' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Petra', label: 'Cat' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Petra', label: 'Mouse' },
    { sampleId: '524', content: 'dmaklwdmkwalmdkl', user: 'Mona', label: 'Cat' }
  ]

  // TODO: user options from real data, display labelnames (not working because of svelte array magic)

</script>

<style>
    .wrapper {
        display: grid;
        grid-template-columns: 1fr 4fr;
        column-gap: 35px;
    }
</style>

<div class="wrapper">
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
