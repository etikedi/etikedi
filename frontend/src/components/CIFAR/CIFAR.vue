<template>
    <section class="section">
        <div class="container">
            <h1 class="title">CIFAR</h1>
            <h2 class="subtitle">Let's go and label this picture!</h2>
            <div class="columns is-desktop is-vcentered">
                <div class="box">
                    <div class="card-content">
                        <img
                            class="image is-128x128 is-horizontal-center"
                            src="https://picsum.photos/200"
                        />
                    </div>
                    Sample-ID: {{ currentSample }}
                    <div class="labeling">
                        <b-field label="Label:">
                            <b-autocomplete
                                class="is-fullwidth"
                                v-model="labelName"
                                :data="labelData"
                                placeholder="Label"
                                clearable
                                @typing="filteredDataArray"
                                @select="option => (selectedLabel = option)"
                            >
                                <template slot="empty"
                                    >No results found</template
                                >
                            </b-autocomplete>
                        </b-field>
                    </div>
                    <div class="field">
                        <button
                            :disabled="selectedLabel == null"
                            v-on:click="sendLabel()"
                            class="button is-info is-fullwidth"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import Vue from "vue";
import {mapActions, mapGetters, mapState} from "vuex";

export default Vue.extend({
    name: "CIFAR",
    props: {},
    data: () => {
        return {
            labelName: "",
            labelData: [],
            selectedLabel: null
        };
    },
    computed: {
        ...mapState("api_default", ["currentSample"]),
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
        ...mapActions(["nextSample", "prevSample", "labelSample"]),

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
            console.log(this.selectedLabel);
            const found = this.labels.find(el => el.name == this.selectedLabel);
            const association = {
                sampleId: this.currentSampleId,
                labelId: found.id,
                userId: "dummy"
            };
            console.log(association);
            this.labelSample(association);
            this.labelName = "";
        }
    }
});
</script>

<style scoped lang="scss">
.box {
    margin: 10px auto;
    max-width: 300px;

    img {
        margin-left: auto;
        margin-right: auto;
    }
}

.container {
    margin: 10px auto;
    width: 800px;
    .title,
    .subtitle {
        text-align: center;
    }

    .labeling {
        margin: 1em 0 1em 0;
    }
}
</style>
