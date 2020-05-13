<template>
    <section class="section">
        <div class="container">
            <div class="columns is-desktop">
                <div class="box">
                    <h1 class="title">CIFAR</h1>
                    <h2 class="subtitle">Let's go and label this picture!</h2>

                    <div class="card-content">
                        <img
                            class="image is-128x128 is-horizontal-center"
                            :src="samples[count].src"
                        />
                    </div>

                    <div class="field">
                        <div class="control">
                            <div class="select is-info is-fullwidth">
                                <select v-model="selected">
                                    <option
                                        v-for="item in labels"
                                        :key="item.id"
                                        :value="item.id"
                                        >{{ item.name }}</option
                                    >
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="field">
                        <button
                            v-on:click="click()"
                            class="button is-info is-fullwidth"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>

            <div class="box">
                <h1 class="title">Create new Label</h1>
                <h2 class="subtitle">Add a new label to the database!</h2>

                <div class="field">
                    <div class="control">
                        <input
                            class="input is-info"
                            type="text"
                            placeholder="Label Name"
                        />
                    </div>
                </div>

                <div class="field">
                    <div class="control">
                        <div class="select is-info is-fullwidth">
                            <select v-model="selectedSampleType">
                                <option
                                    v-for="SampleType in SampleTypes"
                                    :key="SampleType.id"
                                    :value="SampleType.id"
                                    >{{ SampleType.name }}
                                </option>
                            </select>
                        </div>
                    </div>
                </div>

                <button class="button is-info is-fullwidth">
                    Create new Label
                </button>

                <!-- <b-loading
                        :is-full-page="false"
                        :active.sync="loading"
                        :can-cancel="false"
                    ></b-loading> -->
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import Vue from "vue";
import {mapState} from "vuex";

export default Vue.extend({
    name: "CIFAR",
    props: {},
    data: () => {
        const samples = [
            {
                id: 0,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/airplane4.png"
            },
            {
                id: 1,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/dog2.png"
            },
            {
                id: 2,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/automobile4.png"
            },
            {
                id: 3,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/bird6.png"
            },
            {
                id: 4,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/deer6.png"
            },
            {
                id: 5,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/frog10.png"
            },
            {
                id: 6,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/horse2.png"
            },
            {
                id: 7,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/ship1.png"
            },
            {
                id: 8,
                src:
                    "https://www.cs.toronto.edu/~kriz/cifar-10-sample/truck4.png"
            },
            {
                id: 9,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/cat9.png"
            }
        ];

        const labels = [
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

        const SampleTypes = [
            {
                id: 0,
                name: "CIFAR 10"
            },
            {
                id: 1,
                name: "DWTC"
            },
            {
                id: 2,
                name: "Equations"
            },
            {
                id: 3,
                name: "Religious Texts"
            },
            {
                id: 4,
                name: "Resumees"
            }
        ];
        const selected = 0;
        const selectedSampleType = "";
        return {
            samples,
            labels: labels,
            count: 0,
            SampleTypes,
            selected,
            selectedSampleType
        };
    },
    computed: {
        ...mapState(["loading", "cifarSample", "cifarLabels"])
    },
    mounted() {
        // this.$store.dispatch("loadCifarSample");
    },
    methods: {
        click: function() {
            this.count++;
            this.send(this.samples[this.count].id.toString(), this.selected);
        },
        send: function(sampelId: string, labelId: number) {
            /*
            this.$store.dispatch("labelCifarSample", {
                sampelId: id,
                labelId: value
            });
            */

            console.log(labelId);

            if (labelId != null) {
                // send to api
                console.log(
                    `Image with Sample ID <${sampelId}> was assigned to Label ID <${labelId}> and successfully send to server.`
                );
            }
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

.container {
    margin: 10px auto;

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
