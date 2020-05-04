<style scoped lang="scss" src="./style.scss"></style>
<template src="./template.html"></template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
    name: "CIFAR",
    props: {},
    data: () => {
        const images = [
            {
                id: 0,
                src: "https://homepages.cae.wisc.edu/~ece533/images/baboon.png"
            },
            {
                id: 1,
                src: "https://homepages.cae.wisc.edu/~ece533/images/boat.png"
            },
            {
                id: 2,
                src: "https://homepages.cae.wisc.edu/~ece533/images/peppers.png"
            }
        ];
        const labelChunk: string[] = [];
        return {images, labelChunk};
    },
    methods: {
        send: function(id: string, value: string, index: number) {
            /*
            this.$store.dispatch("labelCifarSample", {
                sampleID: id,
                labelID: value
            });
            */
            if (value) {
                // send to api
                alert(
                    `Image with ID <${id}> is labeled with "${value}" and was send successfully to server.`
                );
                (this.$refs[`input-${index}`] as HTMLInputElement[])[0].value =
                    "";
            }
        }
    }
});
</script>
