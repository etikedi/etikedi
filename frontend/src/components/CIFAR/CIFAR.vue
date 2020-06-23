<template>
    <section class="section">
        <center>
            <h1 class="title">CIFAR</h1>
            <h2 class="subtitle">Let's go and label this picture!</h2>
        </center>
        <br />
        <div class="container">
            <div class="columns is-desktop is-vcentered">
                <!-- left preview -->
                <div v-if="count>0" class="box" id="preview" v-on:click="previous()">
                    Sample-ID: {{samples[count-1].id}}
                    <div class="card-content">
                        <img
                            class="image is-64x64 is-horizontal-center"
                            :src="samples[count-1].src"
                        />
                    </div>
                    <div v-if="samples[count-1].labelId != null">
                        Label-ID: {{samples[count-1].labelId}}
                        <br />
                        Label-Name: {{getLabelByID(samples[count-1].labelId).name}}
                    </div>
                </div>

                <div class="box">
                    <div class="card-content">
                        <img
                            class="image is-128x128 is-horizontal-center"
                            :src="samples[count].src"
                        />
                    </div>
                    Sample-ID: {{samples[count].id}}
                    <br />
                    <br />
                    <b-field label="Label:">
                        <b-autocomplete
                            id="input-field"
                            class="is-fullwidth"
                            v-model="labelName"
                            :data="filteredDataArray"
                            placeholder="Label"
                            clearable
                            @select="option => selected = option"
                        >
                            <template slot="empty">No results found</template>
                        </b-autocomplete>
                    </b-field>
                    <div class="field">
                        <button v-on:click="click()" class="button is-info is-fullwidth">Send</button>
                    </div>
                </div>

                <!-- right preview -->
                <div v-if="count+1<=maxCount" class="box" id="preview" v-on:click="next()">
                    Sample-ID: {{samples[count+1].id}}
                    <div class="card-content">
                        <img
                            class="image is-64x64 is-horizontal-center"
                            :src="samples[count+1].src"
                        />
                    </div>
                    <div v-if="samples[count+1].labelId != null">
                        Label-ID: {{samples[count+1].labelId}}
                        <br />
                        Label-Name: {{getLabelByID(samples[count+1].labelId).name}}
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
import {mapGetters, mapState} from "vuex";

export default Vue.extend({
    name: "CIFAR",
    props: {},
    data: () => {
        const samples = [
            {
                id: 0,
                labelId: 0,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/airplane4.png"
            },
            {
                id: 1,
                labelId: null,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/dog2.png"
            },
            {
                id: 2,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/automobile4.png"
            },
            {
                id: 3,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/bird6.png"
            },
            {
                id: 4,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/deer6.png"
            },
            {
                id: 5,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/frog10.png"
            },
            {
                id: 6,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/horse2.png"
            },
            {
                id: 7,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/ship1.png"
            },
            {
                id: 8,
                labelId: null,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/truck4.png"
            },
            {
                id: 9,
                labelId: null,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/cat9.png"
            }
        ];

        const mockLabels = [
            {
                id: 0,
                name: "airplane"
            },
            {
                id: 1,
                name: "car"
            },
            {
                id: 2,
                name: "bird"
            },
            {
                id: 3,
                name: "cat"
            },
            {
                id: 4,
                name: "deer"
            },
            {
                id: 5,
                name: "dog"
            },
            {
                id: 6,
                name: "frog"
            },
            {
                id: 7,
                name: "horse"
            },
            {
                id: 8,
                name: "ship"
            },
            {
                id: 9,
                name: "truck"
            }
        ];

        const count = 0;

        const labelName = "";

        return {
            samples,
            mockLabels,
            labelName,
            count,
            maxCount: samples.length - 1
        };
    },
    computed: {
        ...mapState(["loading", "cifarSample", "cifarLabels"]),
        ...mapGetters(["localLabels", "localImgs"]),
        filteredDataArray() {
            const labels: Array<string> = [];

            for (let i = 0; i < this.mockLabels.length; i++) {
                labels.push(this.mockLabels[i].name);
            }

            return labels.filter(option => {
                return (
                    option
                        .toString()
                        .toLowerCase()
                        .indexOf(this.labelName.toLowerCase()) >= 0
                );
            });
        }
    },
    mounted() {
        // this.$store.dispatch("loadCifarSample");
    },
    methods: {
        click: function() {
            this.send(this.samples[this.count].id, this.labelName);
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
        getLabelByName: function(labelName: string) {
            for (let i = 0; i < this.mockLabels.length; i++) {
                if (labelName == this.mockLabels[i].name) {
                    return this.mockLabels[i];
                }
            }
            return null;
        },
        getLabelByID: function(labelId: string) {
            for (let i = 0; i < this.mockLabels.length; i++) {
                if (labelId == this.mockLabels[i].id) {
                    return this.mockLabels[i];
                }
            }
            return null;
        },
        next: function() {
            if (this.count < this.mockLabels.length - 1) {
                this.count++;
                this.labelName = this.getLabelName(this.count);
                this.focusMethod();
            }
        },
        previous: function() {
            if (this.count > 0) {
                this.count--;
                this.labelName = this.getLabelName(this.count);
                this.focusMethod();
            }
        },
        focusMethod: function getFocus() {
            document.getElementById("input-field").focus();
            (document.getElementById(
                "input-field"
            ) as HTMLInputElement).select();
        },
        getLabelName: function(count: number) {
            if (this.samples[count].labelId != null) {
                return this.getLabelByID(this.samples[count].labelId).name;
            } else return "";
        }
    }
});
</script>

<style scoped lang="scss">
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
