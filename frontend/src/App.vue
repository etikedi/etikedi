<template>
    <div id="app">
        <Header
            title="AERGIA"
            subtitle="Creating labeled datasets like a true lazy greek god."
        />
        <router-view></router-view>
        <Footer
            title="AERGIA"
            homepage="https://wwwdb.inf.tu-dresden.de/"
            author="Dresden Database Systems Group"
            class="foot"
        />
    </div>
</template>

<script lang="ts">
import Vue from "vue";
import VueRouter from "vue-router";
import {mapState} from "vuex";
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import HomePage from "./components/home-page/HomePage.vue";
import LabelView from "@/components/LabelView.vue";

Vue.use(VueRouter);

const Equations = {template: "<p>Platzhalter für Equations</p>"};

const routes = [
    {
        path: "/",
        redirect: "/home"
    },
    {
        path: "/home",
        name: "home",
        component: HomePage
    },
    {
        path: "/label/:datasetId",
        name: "label",
        component: LabelView
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
    },
    components: {
        Header,
        Footer
    }
});
</script>

<style lang="scss">
#app {
    padding-top: 18.25rem;
}

.foot {
    margin-top: 20px;
    margin-left: 20%;
    margin-right: 20%;
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
    "white": (
        $white,
        $black
    ),
    "black": (
        $black,
        $white
    ),
    "light": (
        $light,
        $light-invert
    ),
    "dark": (
        $dark,
        $dark-invert
    ),
    "primary": (
        $info,
        $info-invert
    ),
    "info": (
        $info,
        $info-invert
    ),
    "success": (
        $success,
        $success-invert
    ),
    "warning": (
        $warning,
        $warning-invert
    ),
    "danger": (
        $danger,
        $danger-invert
    ),
    /*"twitter":
        (
            $twitter,
            $twitter-invert
        )
     */
);

// Links
$link: $primary;
$link-invert: $primary-invert;
$link-focus-border: $primary;

// Import Bulma and Buefy styles
@import "~bulma";
@import "~buefy/src/scss/buefy";
</style>
