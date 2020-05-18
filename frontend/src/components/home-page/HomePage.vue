/* eslint-disable prettier/prettier */
<template>
    <div>
        <img src="../../assets/hp.jpeg" class="back"/>
        <div class="para">
            <h1 class="tit">What Is AERGIA</h1>
            <hr class="intro"/>
            <p class="intro">
                Aergia is an innovative labbelling tool powered by active
                learning. It can label DWTC, CIFAR, equations and religious
                text.Aergia is an innovative labbelling tool powered by
                active learning. It can label DWTC, CIFAR, equations and
                religious text.Aergia is an innovative labbelling tool
                powered by active learning. It can label DWTC, CIFAR,
                equations and religious text.
            </p>
        </div>
        <div class="con">
            <div class="columns">
                <div class="column "></div>
                <div class="column">
                    <img
                            class="image is-96x96 i "
                            src="../../assets/hp_label.png"
                    />
                    <b-button class="btn" type="is-dark" outlined
                    >Start Label
                    </b-button
                    >
                </div>
                <div class="column">
                    <img
                            class="image is-96x96 i"
                            src="../../assets/hp_browse.png"
                    />
                    <b-button class="btn" type="is-dark" outlined
                    >Browse
                    </b-button
                    >
                </div>
                <div class="column">
                    <img
                            class="image is-96x96 i"
                            src="../../assets/hp_upload.png"
                    />
                    <b-button class="btn" type="is-dark" outlined
                    >Upload
                    </b-button
                    >
                </div>
                <div class="column "></div>
            </div>
        </div>
    </div>
</template>

<script scoped lang="ts">
    export default {
        name: "HomePage",
        components: {},
        mounted(): void {
            this.$store.commit('setDatasetType', "none")
            this.$store.commit('toggleIsHomePage', true)
        }
    };
</script>

<style lang="scss">
    .con {
        margin-top: 70px;
        margin-left: 15%;
        margin-right: 10%;
        margin-bottom: 30px;
    }

    .intro {
        text-align: center;
        font-size: x-large;
        font-weight: bold;
        margin-left: 30%;
        margin-right: 30%;
        margin-top: 10px;
    }

    .tit {
        text-align: center;
        font-size: xxx-large;
    }

    .intro {
        position: relative;
        text-align: center;
    }

    .btn {
        position: relative;
        margin-top: 50px;
        margin-left: 10px;
    }

    .back {
        position: relative;
        width: 100%;
        height: 600px;
        opacity: 1;
    }
</style>
