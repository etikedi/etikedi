<template>
    <section class="section">
        <div class="container">
            <h1 class="title">{{ cv_id }}</h1>
            <b-button icon-left="chevron-left" @click="prevCv" :disabled=prevButtonDisabled>
                Prev
            </b-button>
            <b-button icon-right="chevron-right" @click="nextCv" :disabled=nextButtonDisabled>
                Next
            </b-button>
            <div>
                <span v-for="(feature, index) in cv.features" :key="index" style="white-sepace: pre-line;">
                    <b-tooltip
                        v-if="feature[0].trim() != '' && !feature[0].includes('<br>')"
                        :label="JSON.stringify(feature[1], null, '\n')"
                        position="is-bottom"
                        size="is-large"
                        multilined>
                        <span v-html="feature[0]" style="border: 1px darkgrey dashed;"></span>
                    </b-tooltip>
                    <span
                        v-else
                        v-html="feature[0]"
                        style="color:red;"
                        >
                    </span>
                </span>
            </div>
            <!-- <pre> -->
                <!-- {{ cv.content}} -->
            <!-- </pre> -->
            <p>
                {{ cv.label }}
            </p>
        </div>
    </section>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
    name: "CV",
    props: {},
    computed: 
        mapState(['cv_id', 'cv', 'prevButtonDisabled', 'nextButtonDisabled'])
        ,
    methods:
        mapActions(['nextCv', 'prevCv']),
    /*mounted() {
        this.fetchCv().catch(error => {
            window.console.error(error);
        });
    },
    methods: {
        async fetchCv() {
            const response = await CV_Service.getCv({cv_id: this.cv_id});
            this.cv = response.data;
        },
        loadNextCv() {
            if (this.cv_id == 1)
                this.prevButtonDisabled = false
            this.cv_id += 1;
        },
        loadPrevCv() {
            if (this.cv_id == 2) {
                this.prevButtonDisabled = true;
                this.cv_id -= 1;
            } else {
                this.cv_id -= 1;
            }
        }
    },
    watch: {
        cv_id: {
            handler: function() {
                this.fetchCv().catch(error => {
                    window.console.error(error)
                })
            }
        }
    }*/
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
