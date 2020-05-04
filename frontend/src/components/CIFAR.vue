<template>
    <section class="section">
        <div class="container">
            <img :src="image" />
            <b-loading :is-full-page="false" :active.sync="loading" :can-cancel="false">
            </b-loading>
        </div>
    </section>
</template>

<script>
import {mapState} from "vuex";

export default {
    name: "CIFAR",
    computed: {
        ...mapState([
            "loading",
            "cifarSample",
            "cifarLabels"
        ])
    },
    mounted() {
        this.$store.dispatch("loadCifarSample");
    }
};
</script>

<style scoped></style>
