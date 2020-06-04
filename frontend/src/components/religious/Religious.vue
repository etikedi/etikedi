<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <span>
                    {{ religiousText }}
                </span>
                <b-loading
                    :is-full-page="false"
                    :active.sync="loading"
                    :can-cancel="false"
                >
                </b-loading>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import {mapState} from "vuex";

export default {
    name: "Religious",
    props: {},
    components: {},
    computed: {
        ...mapState(["religiousText", "loading"]),
        ...mapState("religious", ["religiousText"])
    },
    methods: {},
    mounted(): void {
        this.$store.commit("setDatasetType", "religious");
        this.$store.dispatch("loadDataset");
        this.$store.commit("toggleIsHomePage", false);
        this.$store.commit("toggleShowFeatureTooltipsSwitch", false);
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
