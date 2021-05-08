<script lang="ts">
  import {router} from 'tinro'

  import Button from '../../../ui/Button.svelte'

  import {AceEditor} from "svelte-ace";
  import "brace/mode/python";
  import "brace/theme/chrome";
  import {data, loading as loadingDatasets} from '../../../store/datasets'
  import Card from "../../../ui/Card.svelte";
  import {
    get,
    loading as loadingConfig,
    save,
    testFunctions
  } from "../../../store/LabelingFunctions";
  import {onMount} from "svelte";
  import {notifier} from '@beyonk/svelte-notifications'
  import Table from "../components/labeling/Table.svelte";
  import Image from "../components/labeling/Image.svelte";


  const {id} = router.params()

  let functions: {function_body: string, id: number }[] = null
  let resultLabels = null
  const testContext: {sample: any, testing: boolean, timer: Date, testBtnIcon} = {}
  $: testContext.testBtnIcon = testContext.testing? "pause" : "play"
  const mappings = {
    tables: Table,
    image: Image,
    text: Table,
  }

  $: dataset = $data[id]
  $: loading = $loadingConfig || $loadingDatasets

  onMount(async () => {
    functions = await get(id)
    resultLabels = Array.from({length: functions.length}, (_,i) => null)
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
    const idx = functions.indexOf(func)
    functions = functions.filter(f => f != func)
    resultLabels = resultLabels.filter(r => r != resultLabels[idx])
  }

  function addFunc() {
    // reassigning for svelte reactivity
    let new_func = {function_body: "def foo(sample):\n\treturn \"Dog\"", id: -1}
    functions = [...functions, new_func]
    resultLabels = [...resultLabels, null]
  }

  function startStopTesting() {
    testContext.testing = !testContext.testing;
    if(testContext.testing){
      dryRun()
    }
  }

  async function dryRun() {
    // users my stopped timer between last run and now
    if(testContext.testing) {
      let resp: { result: string[], sample: any } = await testFunctions(id, functions)
      resultLabels = resp.result
      testContext.sample = resp.sample
      setTimeout(dryRun, 3000) // 3 sec
    }
  }

</script>
<div>
  <Button icon="arrow-back-circle-sharp" label="Back" on:click={back}/>
  {#if dataset && functions}
    <h2><b>{dataset.name}</b> Functions</h2>
    <table style="width: 100%">
      <tr>
        {#if testContext.sample != null}
          <td></td>
          <td>
              <div class="data tc">
                <Card>
                {#if Object.keys(mappings).includes(testContext.sample.type)}
                  <svelte:component this={mappings[testContext.sample.type]} data={testContext.sample.content} />
                {:else}
                  <p>Unsupported type {testContext.sample.type}</p>
                {/if}
                </Card>
              </div>
          </td>
          <td></td>
        {/if}
      </tr>
      {#each functions as func, i}
        <tr>
          <td style="width: 70%">
            <div class="editor-container">
              <AceEditor lang="python" value={func.function_body} theme="chrome"
                         width="100%" height="100%" options={{fontSize: "12pt"}}
                         on:input={(obj)=> func.function_body = obj.detail}
              />
            </div>
          </td>
          {#if resultLabels[i] != null}
            <td>
              <div class="result-view">
                {resultLabels[i]}
              </div>
            </td>
          {/if}
          <td>
            <Button icon="trash-outline" label="Delete" on:click={()=>removeFunc(func)}/>
          </td>
        </tr>
      {/each}
    </table>

    <Button icon="add-circle-outline" label="New function" on:click={addFunc}/>
    <Button {loading} disabled={loading} label="Save"
            icon="checkmark-circle-sharp" on:click={saveToBackend}/>
    {#if functions.length > 0}
      <Button {loading} disabled={loading} id="testBtn" label="Test" icon={testContext.testBtnIcon} on:click={startStopTesting}/>
    {/if}
  {:else}
    <div class="loading loading-lg"></div>
  {/if}
</div>

<style>

    td {
        padding:0.7em;
    }
    tr {
        padding: 0.75em 1.5em;
    }

    .data {
        max-height: calc(100vh - 23em);
        overflow: auto;
    }

    .result-view {
        resize: horizontal;
        overflow: auto;
        padding: 0.75em 1.5em;
        background-color: var(--clr-white);
        border-radius: var(--round);
        border: 1px solid #adacac;
        outline: none;
        appearance: none;
        -webkit-appearance: none;
        text-align: center;
        height: 7rem;
    }

    .editor-container {
        resize: both;
        overflow: auto;
        width: 100%;
        height: 7rem;
    }

    .actions > a {
        margin-left: 1.25rem;
    }

    ion-icon {
        font-size: 1.5rem;
    }

</style>