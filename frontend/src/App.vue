<template>
    <section id="app" class="section">
            <HelloWorld msg="Welcome to Your Vue.js App" content="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eligendi non quis exercitationem culpa nesciunt nihil aut nostrum explicabo reprehenderit optio amet ab temporibus asperiores quasi cupiditate. Voluptatum ducimus voluptates voluptas?" />
    </section>
</template>

<script>
import HelloWorld from "./components/HelloWorld.vue";

export default {
    name: "app",
    components: {
        HelloWorld
    }
};
</script>

<style lang="scss">
/*#app {
margin-top: 60px;
}*/
</style>
