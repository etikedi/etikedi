/* eslint-disable prettier/prettier */
<template>
    <div id="app">
        <Header
            title="AERGIA"
            subtitle="Creating labeled datasets like a true lazy greek god."
            @updateObjectType="updateBody"
        />
        <p v-if="this.objectType==1">Platzhalter für CIFAR</p>
        <p v-if="this.objectType==2">Platzhalter für DWTC</p>
        <p v-if="this.objectType==3">Platzhalter für Equations</p>
        <p v-if="this.objectType==4">Platzhalter für Religious Texts</p>
        <CV v-if="this.objectType==5"/>
        <Footer
            title="AERGIA"
            homepage="https://jgonsior.de"
            author="Julius Gonsior"
        />
    </div>
</template>

<script lang="ts">
import Vue from "vue";
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import CV from "./components/CV.vue";

export default Vue.extend({
    name: "app",
    data: function () {
            return {
                objectType: 0
            }
    },
    components: {
        Header,
        Footer,
        CV
    },
    methods:{
        updateBody: function(objectType){
            switch (objectType) {
                case "1":{
                    //methods for CIFAR
                    break;
                }
                case "2":{
                    //methods for DWTC
                    break;
                }
                case "3":{
                    //methods for Equations
                    break;
                }
                case "4":{
                    //methods for Religious Texts
                    break;
                }
                case "5":{
                    this.$store.dispatch('loadCv');
                    break;
                }
                default: {
                    break;
                }
            }
            this.objectType = objectType;

        }
    }    
    /*mounted() {
        this.$store.dispatch('loadCv');
    }*/
});
</script>

<style lang="scss">
#app {
    padding-top: 18.25rem;
}

// Import Bulma's core
@import "~bulma/sass/utilities/_all";

// Set your colors
//$primary: #8c67ef;
$primary: $info;
$primary-invert: findColorInvert($primary);
//$twitter: #4099FF;
//$twitter-invert: findColorInvert($twitter);

// Setup $colors to use as bulma classes (e.g. 'is-twitter')
$colors: (
    "white": ($white, $black),
    "black": ($black, $white),
    "light": ($light, $light-invert),
    "dark": ($dark, $dark-invert),
    "primary": ($info, $info-invert),
    "info": ($info, $info-invert),
    "success": ($success, $success-invert),
    "warning": ($warning, $warning-invert),
    "danger": ($danger, $danger-invert),
    //"twitter": ($twitter, $twitter-invert)
);

// Links
$link: $primary;
$link-invert: $primary-invert;
$link-focus-border: $primary;

// Import Bulma and Buefy styles
@import "~bulma";
@import "~buefy/src/scss/buefy";
</style>
