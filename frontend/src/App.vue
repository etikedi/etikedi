<template>
    <div id="app">
        <Header title="AERGIA" subtitle="Creating labeled datasets like a true lazy greek god."/>
        <CV />
        <Footer title="AERGIA" homepage="https://jgonsior.de" author="Julius Gonsior"/>
    </div>
</template>

<script>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import CV from "./components/CV.vue";

export default {
    name: "app",
    components: {
        Header,
        Footer,
        CV
    },
    mounted() {
        this.$store.dispatch('loadCv');
    }


};
</script>

<style lang="scss">

#app {
    //padding-top: 12.25rem;
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
 //   "twitter": ($twitter, $twitter-invert)
);

// Links
$link: $primary;
$link-invert: $primary-invert;
$link-focus-border: $primary;

// Import Bulma and Buefy styles
@import "~bulma";
@import "~buefy/src/scss/buefy";
</style>
