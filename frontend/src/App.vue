<template>
    <div id="app">
        <Header
            title="AERGIA"
            subtitle="Creating labeled datasets like a true lazy greek god."
            @updateDatasetType="updateDatasetType"
        />
        <router-view></router-view>
        <Footer
            title="AERGIA"
            homepage="https://jgonsior.de"
            author="Julius Gonsior"
        />
    </div>
</template>

<script lang="ts">
import Vue from "vue";
import VueRouter from "vue-router";
import {mapState} from 'vuex';
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import CV from "./components/CV/CV.vue";
import DWTC from "./components/dwtc/DWTC.vue";
import LandingPage from "./components/landing-page/LandingPage.vue";

Vue.use(VueRouter);

const Cifar = { template: "<p>Platzhalter für CIFAR</p>" }
const Equations = { template: "<p>Platzhalter für Equations</p>" }
const ReligiousTexts = { template: "<p>Platzhalter für Religious Texts</p>" }

const routes = [
    {
        path: "/",
        redirect: "/home"
    },
    {
        path: "/home",
        name: "home",
        component: LandingPage
    },
    {
        path: "/cifar",
        name: "cifar",
        component: Cifar
    },
    {
        path: "/dwtc",
        name: "dwtc",
        component: DWTC
    },
    {
        path: "/equations",
        name: "equations",
        component: Equations
    },
    {
        path: "/religious-texts",
        name: "religious-texts",
        component: ReligiousTexts
    },
    {
        path: "/cv",
        name: "cv",
        component: CV
    }
];

const router = new VueRouter({
    mode: "history",
    routes
});

export default Vue.extend({
    router,
    name: "app",
    computed: {
            ...mapState(['datasetType']),
    },
    components: {
        Header,
        Footer
    },
    methods:{
        updateDatasetType: function(objectType: any){

			this.$store.commit('setDatasetType', objectType)
			this.$store.dispatch('loadDataset')
        }
    },
    mounted() {
        this.$store.dispatch('loadDataset');
    }
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
