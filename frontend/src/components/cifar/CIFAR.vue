<style scoped lang="scss" src="./style.scss"></style>
<template src="./template.html"></template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
    name: "CIFAR",
    props: {},
    data: () => {
        const samples = [
            {
                id: 0,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/airplane4.png"
            },
            {
                id: 1,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/dog2.png"
            },
            {
                id: 2,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/automobile4.png"
            },
            {
                id: 3,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/bird6.png"
            },
            {
                id: 4,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/deer6.png"
            },
            {
                id: 5,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/frog10.png"
            },
            {
                id: 6,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/horse2.png"
            },
            {
                id: 7,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/ship1.png"
            },
            {
                id: 8,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/truck4.png"
            },
            {
                id: 9,
                src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/cat9.png"
            },
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
        
        return {samples, lables, count:0};

    },
    methods: {
        send: function(sampleId: string, lableId: number) {
            /*
            this.$store.dispatch("labelCifarSample", {
                sampleId: id,
                lableId: value
            });
            */
            if (lableId != null) {
                // send to api
                alert(
                    `Image with Sample ID <${sampleId}> was assigned to Lable ID <${lableId}> and successfully send to server.`
                );
                (this.$refs[`input-${lableId}`] as HTMLInputElement[])[0].value = "";
            }
        }
    }
});
</script>
