<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <span>
                    {{religiousText}}
                </span>
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
        name: "Religious",
        props: {},
        components: {},
        computed: {
            ...mapState(['religiousText', 'loading']),
            ...mapState('religious', ['religiousText']),
        },
        methods: {
        }

    };
</script>

<style scoped lang="scss">
    .loading-overlay {
        left: 0;
        top: 0;
        position: fixed;
        transform: translateX(-50%, -50%);
    }
</style>
