<script lang="ts">
  import {router} from 'tinro'

  import Button from '../../../ui/Button.svelte'

  import {AceEditor} from "svelte-ace";
  import "brace/mode/python";
  import "brace/theme/chrome";
  import {data, loading as loadingDatasets} from '../../../store/datasets'
  import Card from "../../../ui/Card.svelte";
  import {get, loading as loadingConfig, save} from "../../../store/LabelingFunctions";
  import {onMount} from "svelte";
  import {notifier} from '@beyonk/svelte-notifications'


  const {id} = router.params()

  let functions = null

  $: dataset = $data[id]
  $: loading = $loadingConfig || $loadingDatasets

  onMount(async () => {
    functions = await get(id)
  })

  async function saveToBackend() {
    if (loading) return
    try {
      await save(id, functions)
      notifier.success('Saved')
    } catch (e) {
      console.error(e)
      notifier.danger(e.message)
    }
  }

  function back() {
    router.goto('../../')
  }

  function removeFunc(func) {
    // reassigning for svelte reactivity
    functions = functions.filter(f => f != func)
  }

  function addFunc() {
    // reassigning for svelte reactivity
    let new_func = {function_body: "#Enter new function"}
    functions = [...functions, new_func]
  }
</script>
<div>
  <Button icon="arrow-back-circle-sharp" label="Back" on:click={back}/>
  {#if dataset && functions}
    <h2><b>{dataset.name}</b> Functions</h2>

    {#each functions as func}
      <Card>
        <div class="flex justify-between">
          <div class="editor-container">
          <AceEditor lang="python" value={func.function_body} theme="chrome"
                       width="100%" height="100%"
                       on:input={(obj)=> func.function_body = obj.detail}
            />
          </div>
          <Button icon="trash-outline" label="Delete" on:click={()=>removeFunc(func)}/>
        </div>
      </Card>
    {/each}
    <Button icon="add-circle-outline" label="New function" on:click={addFunc}/>
    <Button {loading} disabled={loading} label="Save"
            icon="checkmark-circle-sharp" on:click={saveToBackend}/>
  {:else}
    <div class="loading loading-lg"></div>
  {/if}
</div>

<style>

    .editor-container{
        resize: both;
        overflow: auto;
        width: 90%;
        height: 100px;
    }

    .actions > a {
        margin-left: 1.25rem;
    }

    ion-icon {
        font-size: 1.5rem;
    }

</style>