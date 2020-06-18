<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <span>
                    {{ currentSample }}
                </span>
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
        ...mapState("api_default", ["currentSample"])
    },
    methods: {},
    //mounted(): void {
    //}
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
