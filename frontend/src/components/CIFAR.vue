<template>
    <section class="section">
        <div class="container">
            <img :src="image" />
        </div>
    </section>
</template>

<script>
import {mapState} from "vuex";
export default {
    name: "CIFAR",
    computed: {
        ...mapState(["image"])
    },
    methods: {
        loadImage: function(event) {
            console.log(event);
        }
    }
};
</script>

<style scoped></style>
