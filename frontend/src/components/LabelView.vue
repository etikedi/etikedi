<template>
    <article>
        <!-- here go datasetType views -->
        <CV v-if="datasetType == 'cv'" />
        <DWTC v-if="datasetType == 'dwtc'" />
        <PlainText v-if="datasetType == 'religious'" />
        <CIFAR v-if="datasetType == 'cifar'" />

        <div class="search-container">
            <div class="labeling">
                <b-field label="Search labels:">
                    <b-autocomplete
                        class="is-fullwidth"
                        v-model="labelName"
                        :data="labelData"
                        placeholder="Label"
                        clearable
                        @typing="filteredDataArray"
                        @select="option => (selectedLabel = option)"
                    >
                        <template slot="empty">No results found</template>
                    </b-autocomplete>
                </b-field>
            </div>
            <div class="send">
                <button
                    :disabled="selectedLabel == null"
                    v-on:click="sendLabel()"
                    class="button is-info is-fullwidth"
                >
                    Send
                </button>
            </div>
        </div>

        <!-- fallback for dataset type "none" -->
        <section class="section" v-if="datasetType == 'none'">
            <div class="container">
                <div style="position: relative;">
                    <span>
                        No dataset selected!
                    </span>
                </div>
            </div>
        </section>

        <section class="center"></section>

        <b-loading
            :is-full-page="false"
            :active.sync="loading"
            :can-cancel="false"
        >
        </b-loading>
    </article>
</template>

<script lang="ts">
import {mapState, mapActions, mapGetters} from "vuex";
import store from "@/store";

import CV from "@/components/CV/CV.vue";
import DWTC from "@/components/dwtc/DWTC.vue";
import PlainText from "@/components/dst_plaintext/PlainText.vue";
import CIFAR from "@/components/CIFAR/CIFAR.vue";
import {labelSample} from "@/store/actions";

export default {
    name: "LabelView",
    components: {
        CV,
        DWTC,
        PlainText,
        CIFAR
    },
    props: {},
    data: () => {
        return {
            labelName: "",
            labelData: [],
            selectedLabel: null
        };
    },
    computed: {
        ...mapState("api_default", ["currentSampleId"]),
        ...mapState([
            "datasets",
            "activeDatasetId",
            "activeDataset",
            "loading",
            "labels"
        ]),
        ...mapGetters([
            "datasetType",
            "sampleShortTitle",
            "prevButtonDisabled",
            "nextButtonDisabled"
        ])
    },
    methods: {
        ...mapActions(["labelSample"]),
        filteredDataArray() {
            const filteredLabels: Array<string> = [];

            for (let i = 0; i < this.labels.length; i++) {
                filteredLabels.push(this.labels[i].name);
            }

            this.labelData = filteredLabels.filter(option => {
                return (
                    option
                        .toString()
                        .toLowerCase()
                        .indexOf(this.labelName.toLowerCase()) >= 0
                );
            });
        },

        sendLabel: function() {
            const found = this.labels.find(el => el.name == this.selectedLabel);
            const association = {
                sampleId: this.currentSampleId,
                labelId: found.id,
                userId: "dummy"
            };
            console.log("Association available to be sent:");
            console.log(association);
            this.labelSample(found.id);
            this.labelName = "";
        }
    },
    watch: {
        $route: function(to, from) {
            // react to route changes...
            console.log(
                "Route changed - setting activeDatasetId to " +
                    this.$route.params.datasetId
            );
            this.$store.commit(
                "setActiveDatasetId",
                this.$route.params.datasetId
            );
            this.$store.dispatch("updateActiveDataset");
        }
    },
    mounted(): void {
        console.log(
            "mounting LabelView - setting activeDatasetId to " +
                this.$route.params.datasetId
        );
        this.$store.commit("setActiveDatasetId", this.$route.params.datasetId);
        this.$store.dispatch("updateActiveDataset");
    },
    beforeDestroy(): void {
        console.log("destroying LabelView - unsetting activeDatasetId");
        this.$store.commit("setActiveDatasetId", null);
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
#navbarMenuHeroA {
}

.search-container {
    height: 8em;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;

    .labeling {
        width: 13em;
    }

    .send {
        width: 13em;
    }
}

.sticky {
    position: fixed;
    top: 0;
    width: 100%;
}

.sticky + .section {
    padding-top: 3rem;
}
</style>
