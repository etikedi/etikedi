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
                    Sample-ID: {{currentSample}}
                    <b-field label="Label:">
                        <b-autocomplete
                                class="is-fullwidth"
                                v-model="labelName"
                                :data="labelData"
                                placeholder="Label"
                                clearable
                                @typing="filteredDataArray"
                                @select="option => selectedLabel = option"
                        >
                            <template slot="empty">No results found</template>
                        </b-autocomplete>
                    </b-field>
                    <div class="field">
                        <button :disabled="selectedLabel == null" v-on:click="sendLabel()" class="button is-info is-fullwidth">Send</button>
                    </div>
                </div>
            </div>

            <!-- <b-loading
                        :is-full-page="false"
                        :active.sync="loading"
                        :can-cancel="false"
            ></b-loading>-->
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
            selectedLabel: null,
        };
    },
    computed: {
        ...mapState("api_default", ["currentSample"]),
        ...mapState("api_default", ["currentSampleId"]),
        ...mapState(["datasets", "activeDatasetId", "activeDataset", "loading", "labels"]),
        ...mapGetters(["datasetType", "sampleShortTitle", "prevButtonDisabled", "nextButtonDisabled"]),
    },
    //mounted() {
        // this.$store.dispatch("loadCifarSample");
    //},
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
            //this.send(this.samples[this.count].id, this.labelName);
        },

        send: function(sampelId: number, labelName: string) {
            if (labelName != "") {
                const label = this.getLabelByName(labelName);
                if (label != null) {
                    this.samples[sampelId].labelId = label.id;
                    console.log(
                        `Image with Sample ID <${sampelId}> was assigned to Label "${labelName}" and successfully send to server.`
                    );
                    this.next();
                } else {
                    console.log(
                        `Label with name "${labelName}" was not found!`
                    );
                }
                this.focusMethod();
            }
        },
    }
});
</script>

<style scoped lang="scss">

#testbox {
    width: 100%;
    height: 500px;
}
.loading-overlay {
    left: 0;
    top: 0;
    position: fixed;
    transform: translateX(-50%, -50%);
}

.box {
    margin: 10px auto;
    max-width: 300px;

    img {
        margin-left: auto;
        margin-right: auto;
    }
}

#preview {
    opacity: 0.4;
    height: 250px;
    width: 200px;
}

.container {
    margin: 10px auto;
    width: 800px;
    .title,
    .subtitle {
        text-align: center;
    }

    .image-container {
        margin: 10px auto;
        max-width: 300px;

        .label {
            margin: 10px 0 0 0;

            .button {
                width: 100%;
            }
        }
    }
}
</style>
