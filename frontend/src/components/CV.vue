<template>
    <section class="section">
        <div class="container">
            <div>
                <span v-for="(feature, index) in cv.features" :key="index" style="white-sepace: pre-line;">
                    <b-tooltip
                        v-if="feature[0].trim() != '' && !feature[0].includes('<br>')"
                        :label="JSON.stringify(feature[1], null, '\n')"
                        position="is-bottom"
                        size="is-large"
                        type="is-info"
                        multilined>
                        <span v-html="feature[0]" style="border: 1px darkgrey dashed;"></span>
                    </b-tooltip>
                    <span
                        v-else
                        v-html="feature[0]"
                        >
                    </span>
                </span>
            </div>
        </div>
    </section>
</template>

<script>
import { mapState } from 'vuex';

export default {
    name: "CV",
    props: {},
    computed: 
        mapState(['cv'])
        ,
};
</script>

<style scoped lang="scss">
</style>
