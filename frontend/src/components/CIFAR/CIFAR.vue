<template>
    <section class="section">
        <div class="container">
            <h1 class="title">CIFAR</h1>
            <h2 class="subtitle">Let's go and label this picture!</h2>
            <div class="columns is-desktop is-vcentered">
                <div class="box">
                    <div class="card-content">
                        <img
                            class="image is-128x128 is-horizontal-center"
                            v-bind:src="
                                'data:image/png;base64,' + currentSample
                            "
                        />
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import Vue from "vue";
import {mapState} from "vuex";

export default Vue.extend({
    name: "CIFAR",
    props: {},
    computed: {
        ...mapState("api_default", ["currentSample"])
    }
});
</script>

<style scoped lang="scss">
.box {
    margin: 10px auto;
    max-width: 300px;

    img {
        margin-left: auto;
        margin-right: auto;
    }
}

.container {
    margin: 10px auto;
    width: 800px;
    .title,
    .subtitle {
        text-align: center;
    }
}
</style>
