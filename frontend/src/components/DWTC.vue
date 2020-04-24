<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <table class="table" v-html="dwtc">
                </table>
                <b-loading
                        :is-full-page="false"
                        :active.sync="loading"
                        :can-cancel="false">
                </b-loading>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
    import {mapState} from 'vuex';

    export default {
        name: "DWTC",
        props: {},
        components: {},
        computed: {
            ...mapState(['dwtc', 'loading']),
        },
        methods: {}
    };
</script>

<style scoped lang="scss">
table {
    width: 100%;
}
</style>