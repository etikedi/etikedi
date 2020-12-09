<script lang="ts">
  let data, features, displayFiles
  let files = []

  function initFiles(input) {
    files = Array.from(input.files)
    let output = []
    files.forEach((file) => {
      output.push(
        '<li><strong>',
        escape(file.name),
        '</strong> (',
        file.type || 'n/a',
        ') - ',
        file.size,
        ' bytes, last modified: ',
        file.lastModifiedDate.toLocaleDateString(),
        '</li>'
      )
    })
    displayFiles.innerHTML = '<ul>' + output.join('') + '</ul>'
  }

  function upload() {
    if (files.length === 0) {
      console.error('No files chosen!')
      return
    }
    files.forEach((file) => {
      const reader = new FileReader()

      reader.addEventListener('error', (err) => {
        console.error('FileReader error' + err)
      })

      reader.onload = (ev) => {
        // Send result
        console.log(ev)
      }

      reader.readAsArrayBuffer(file)

      console.log(reader)
    })
  }
</script>

<style>
  .cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 10px;
    margin-bottom: 10px;
  }

  .card {
    padding: 30px;
    border-radius: 15px;
    border: 3px solid #032557;
    align-items: center;
  }

  ion-icon {
    color: #000;
    width: 4.5em;
    height: 4.5em;
    margin-bottom: 2em;
  }

  span {
    font-size: 2.5em;
    font-weight: lighter;
  }

  .btn {
    color: #3b4351;
    height: initial;
    width: 100%;
  }
</style>

<h1>Upload</h1>
<input
  type="file"
  bind:this={data}
  style="display: none"
  multiple
  accept="application/json"
  on:input={() => initFiles(data)} />
<input
  type="file"
  bind:this={features}
  style="display: none"
  multiple
  accept="image/*"
  on:input={() => initFiles(features)} />
<div class="cards">
  <div>
    <button class="card btn" on:click={data.click()}>
      <ion-icon name="folder" />
      <span>Data</span>
    </button>
  </div>
  <div>
    <button class="card btn" on:click={features.click()}>
      <ion-icon name="document" />
      <span>Features</span>
    </button>
  </div>
</div>
<div bind:this={displayFiles} />
<button class="btn card" on:click={upload}> <span>Upload</span> </button>
