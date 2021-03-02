<script>
  import Button from '../../../ui/Button.svelte'

  let alRandom, alParameters

  function play() {
    if (alRandom.paused && alParameters.paused) {
      alRandom.play()
      alParameters.play()
    } else {
      alRandom.pause()
      alParameters.pause()
    }
  }
</script>

<style>
    .wrapper {
        height: 30em;
        display: grid;
        grid-template-columns: 1fr 1fr;
        column-gap: 10px;
    }

    .wrapper div, .button {
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>

<div class="wrapper">
  <div>
    <video bind:this={alRandom} width="320" height="240">
      <source src="/video/al_random.mov" type="video/mp4">
      Your browser does not support the video tag.
    </video>
  </div>
  <div>
    <video bind:this={alParameters} width="320" height="240">
      <source src="/video/al_parameter.mov" type="video/mp4">
      Your browser does not support the video tag.
    </video>
  </div>
</div>
<div class="button">
  <Button icon="play-circle-sharp" label="Start simulation" on:click={play}/>
</div>