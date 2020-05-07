<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <h1 class="title">CIFAR</h1>
                <h2 class="subtitle">Let's go and label your pics!</h2>

                <div class="columns is-desktop">
                    <div class="image-container column">
                        <figure class="image is-128x128">
                            <img :src="samples[count].src" />
                        </figure>

                        <div class="label">
                            <div class="columns">
                                <div class="column">
                                    <div class="select">
                                        <select v-model="selected">
                                            <option
                                                v-for="item in lables"
                                                :key="item.id"
                                                :value="item.id"
                                                >{{ item.name }}</option
                                            >
                                        </select>
                                    </div>
                                </div>

                                <div class="column">
                                    <button
                                        v-on:click="
                                            count++;
                                            send(samples[count].id, selected);
                                        "
                                        class="button is-info"
                                    >
                                        Send
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
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

        const lables = [
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

        return {samples, lables, count: 0};
    },
    computed: {
        ...mapState(["loading", "cifarSample", "cifarLabels"])
    },
    mounted() {
        this.$store.dispatch("loadCifarSample");
    },
    methods: {
        send: function(sampleId: string, lableId: number) {
            /*
            this.$store.dispatch("labelCifarSample", {
                sampleId: id,
                lableId: value
            });
            */

            console.log(lableId);

            if (lableId != null) {
                // send to api
                alert(
                    `Image with Sample ID <${sampleId}> was assigned to Lable ID <${lableId}> and successfully send to server.`
                );
                (this.$refs[
                    `input-${lableId}`
                ] as HTMLInputElement[])[0].value = "";
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
