<script>

    const actions = [
        {
            header: 'Label',
            text: 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.',
            img: './img/label.png'
        }, {
            header: 'Select',
            text: 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.',
            img: './img/select.png'
        }, {
            header: 'Annotate',
            text: 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.',
            img: './img/annotate.png'
        }
    ]
</script>

<style>
    .wrapper {
        display: grid;
        grid-template-columns: 1.3fr 1fr;
        column-gap: 2em;
        margin: 5em 0;
        align-items: center;
    }

    .text {
        display: flex;
        flex-direction: column;
    }

    img {
        width: 100%;
        border-radius: 15px;
    }
</style>

{#each actions as action, i}
    <div class="wrapper">
        {#if i % 2 !== 0}
            <img src={action.img} alt="Landing">
        {/if}
        <div class="text">
            <h2>{action.header}</h2>
            <span>{action.text}</span>
        </div>
        {#if i % 2 === 0}
            <img src={action.img} alt="Landing">
        {/if}
    </div>
{/each}
