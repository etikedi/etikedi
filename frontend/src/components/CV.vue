<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <span
                    v-for="(feature, index) in cv.features"
                    :key="index"
                    :feature_id="index"
                    style="white-sepace: pre-line;"
                >
                    <template
                        v-if="
                            feature[0].trim() != '' &&
                                !feature[0].includes('<br>')
                        "
                    >
                        <template v-if="displayFeatureTooltips">
                            <b-tooltip
                                :label="JSON.stringify(feature[1], null, '\n')"
                                position="is-bottom"
                                size="is-large"
                                type="is-info"
                                multilined
                            >
                                <Feature
                                    :text="feature[0]"
                                    :label="feature[1]['label']"
                                />
                            </b-tooltip>
                        </template>
                        <template v-else>
                            <!-- this is important but only for cosmetic reasons -->
                            <Feature
                                :text="feature[0]"
                                :label="feature[1]['label']"
                            />
                        </template>
                    </template>
                    <template v-else>
                        <span v-html="feature[0]"> </span>
                    </template>
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
import Feature from "@/components/Feature.vue";
import {mapState} from "vuex";

export default {
    name: "CV",
    props: {},
    components: {Feature},
    computed: {
        ...mapState(["cv", "loading", "displayFeatureTooltips"])
    },
    methods: {
        labelClass: function(feature: Array<any>) {
            window.console.log(feature[1]["label"]);
            return feature[1]["label"];
        }
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
