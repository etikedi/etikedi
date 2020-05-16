/* eslint-disable prettier/prettier */
<template>
    <div id="HomePage">
        <b-navbar>
            <template slot="start">
                <b-navbar-item href="#">
                    Home
                </b-navbar-item>
                <b-navbar-item href="#">
                    Label
                </b-navbar-item>
                <b-navbar-item href="#">
                    Upload
                </b-navbar-item>
                <b-navbar-item href="#">
                    Browse
                </b-navbar-item>

                <b-navbar-dropdown label="Info" class="is-info">
                    <b-navbar-item href="#">
                        About
                    </b-navbar-item>
                    <b-navbar-item href="#">
                        Contact
                    </b-navbar-item>
                </b-navbar-dropdown>
            </template>

            <template slot="end">
                <b-navbar-item tag="div">
                    <div class="buttons">
                        <a class="button is-info">
                            <strong>Sign up</strong>
                        </a>
                        <a class="button is-light">
                            Log in
                        </a>
                    </div>
                </b-navbar-item>
            </template>
        </b-navbar>
        <body>
            <img src="../assets/hp.jpeg" class="back" />
            <div class="para">
                <h1 class="tit">What Is AERGIA</h1>
                <hr class="intro" />
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
                            src="../assets/hp_label.png"
                        />
                        <b-button class="btn" type="is-dark" exxpanded outlined
                            >Start Label</b-button
                        >
                    </div>
                    <div class="column">
                        <img
                            class="image is-96x96 i"
                            src="../assets/hp_browse.png"
                        />
                        <b-button class="btn" type="is-dark" outlined
                            >Browse</b-button
                        >
                    </div>
                    <div class="column">
                        <img
                            class="image is-96x96 i"
                            src="../assets/hp_upload.png"
                        />
                        <b-button class="btn" type="is-dark"  outlined
                            >Upload</b-button
                        >
                    </div>
                    <div class="column "></div>
                </div>
            </div>
            <Footer
                title="AERGIA"
                homepage="https://wwwdb.inf.tu-dresden.de/"
                author="by Dresden Database Systems Group"
                class="foot"
            ></Footer>
        </body>
    </div>
</template>

<script scoped lang="ts">
import Footer from "../components/Footer.vue";
export default {
    name: "HomePage",
    components: {
        Footer
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
.foot {
    margin-top: 20px;
    margin-left: 20%;
    margin-right: 20%;
}
</style>
