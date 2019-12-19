<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <span 
                    v-for="(feature, index) in cv.features" 
                    :key="index"
                    :id="index"
                    style="white-sepace: pre-line;">
                    <template v-if="feature[0].trim() != '' && !feature[0].includes('<br>')">
                        <template v-if="display_feature_tooltips">
                            <b-tooltip
                                :label="JSON.stringify(feature[1], null, '\n')"
                                position="is-bottom"
                                size="is-large"
                                type="is-info"
                                multilined>
                                <Feature :text="feature[0]" label="feature[1]['label']" /> 
                            </b-tooltip>
                        </template>
                        <template v-else>
                            <!-- this is important but only for cosmetic reasons -->
                            <span class="is-large is-info b-tooltip">
                                <Feature :text="feature[0]" label="feature[1]['label']" /> 
                            </span>
                        </template>
                    </template>
                    <template v-else>
                        <span v-html="feature[0]">
                        </span>
                    </template>
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

<script>
import Feature from "@/components/Feature.vue";
import { mapState } from 'vuex';

export default {
    name: "CV",
    props: {},
    components: {Feature},
    computed: { 
        ...mapState(['cv', 'loading', 'display_feature_tooltips']),
    },
    methods: {
        labelClass: function(feature) {
            window.console.log(feature[1]['label']);
            return feature[1]['label'];
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
