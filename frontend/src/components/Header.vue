<template>
    <header>
        <nav
            class="navbar is-fixed-top hero is-info is-bold"
            role="navigation"
            aria-label="main navigation"
        >
            <div class="hero-head">
                <div class="container">
                    <b-navbar>
                        <template slot="start">
                            <b-navbar-item href="#">
                                <router-link to="/home">Home</router-link>
                            </b-navbar-item>
                            <b-navbar-dropdown label="Label">
                                <b-navbar-item
										v-for="(dataset, datasetId) in datasets"
										:key="datasetId"
										:href="'/label/' + datasetId"
										style="color: #000000;">
                                    {{ dataset.name }}
                                </b-navbar-item>
                            </b-navbar-dropdown>
                            <b-navbar-item href="#">
                                Upload
                            </b-navbar-item>
                            <b-navbar-item href="#">
                                Browse
                            </b-navbar-item>

                            <b-navbar-dropdown label="Info">
                                <b-navbar-item href="#" style="color: #000000;">
                                    About
                                </b-navbar-item>
                                <b-navbar-item href="#" style="color: #000000;">
                                    Contact
                                </b-navbar-item>
                            </b-navbar-dropdown>
                        </template>

                        <template slot="end" class="ml-auto">
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
                </div>
            </div>
            <div class="hero-body">
                <div class="container">
                    <h1 class="title">{{ title }}</h1>
                    <p class="subtitle">
                        {{ subtitle }}
                    </p>
                </div>
            </div>
        </nav>
    </header>
</template>

<script lang="ts">
import {mapState, mapActions, mapGetters} from "vuex";
import store from "@/store";

export default {
    name: "Header",
    props: {
        title: String,
        subtitle: String
    },
    computed: {
		...mapState(["datasets"]),
    },
    methods: {
    },
    mounted(): void {
        this.$store.dispatch("loadAllDatasets");
    },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
#navbarMenuHeroA {
}

.sticky {
    position: fixed;
    top: 0;
    width: 100%;
}

.sticky + .section {
    padding-top: 3rem;
}
</style>
