<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <table class="table" v-html="currentSample"></table>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import Vue from "vue";
import {mapState} from "vuex";

export default Vue.extend( {
    name: "DWTC",
    props: {},
    computed: {
        ...mapState("api_default", ["currentSample"]),
    }
});
</script>

<style scoped lang="scss">
table {
    width: 100%;
}
</style>
