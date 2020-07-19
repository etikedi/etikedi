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
                            <b-navbar-item @click="route('/home')">Home</b-navbar-item>
                            <b-navbar-dropdown label="Label">
                                <b-navbar-item
                                    v-for="(dataset, datasetId) in datasets"
                                    :key="datasetId"
                                    @click="route('/label/' + datasetId)"
                                    style="color: #000000;"
                                >{{ dataset.name }}</b-navbar-item>
                            </b-navbar-dropdown>
                            <b-navbar-item href="#">Upload</b-navbar-item>
                            <b-navbar-item href="#">Browse</b-navbar-item>

                            <b-navbar-dropdown label="Info">
                                <b-navbar-item
                                    @click="route('/about')"
                                    style="color: #000000;"
                                >About</b-navbar-item>
                                <b-navbar-item
                                    @click="route('/contact')"
                                    style="color: #000000;"
                                >Contact</b-navbar-item>
                            </b-navbar-dropdown>
                        </template>

                        <template slot="end" class="ml-auto">
                            <b-navbar-item tag="div" @click="route('/signup')">
                                <div class="buttons">
                                    <a class="button is-info">
                                        <strong>Sign up</strong>
                                    </a>
                                    <a class="button is-light" @click="dummyLogin">Log in</a>
                                </div>
                            </b-navbar-item>
                        </template>
                    </b-navbar>
                </div>
            </div>
            <div class="hero-body">
                <div class="container">
                    <h1 class="title">{{ title }}</h1>
                    <p class="subtitle">{{ subtitle }}</p>
                </div>
            </div>

            <!-- header component of LabelView, only shown when activeDatasetId set (see labelView) -->
            <div class="hero-foot" v-if="activeDatasetId != null">
                <div class="container">
                    <div id="navbarMenuHeroA" class="navbar-menu">
                        <div class="navbar-start">
                            <b-button
                                class="navbar-item"
                                tag="a"
                                type="is-link"
                                icon-left="chevron-left"
                                @click="prevSample"
                                :disabled="prevButtonDisabled"
                                inverted
                                outlined
                            >Prev</b-button>
                            <h2
                                class="title"
                                style="padding: 0 1rem 0 1rem"
                            >{{ $store.getters.sampleShortTitle }}</h2>
                            <b-button
                                class="navbar-item"
                                tag="a"
                                type="is-link"
                                icon-right="chevron-right"
                                @click="nextSample"
                                :disabled="nextButtonDisabled"
                                inverted
                                outlined
                            >Next</b-button>
                        </div>
                        <div class="navbar-end">
                            <b-button
                                v-for="(label, index) in labels"
                                :key="index"
                                class="navbar-item"
                                tag="a"
                                type="is-link"
                                @click="labelSample(label.id)"
                                inverted
                                outlined
                            >{{ label.name }}</b-button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    </header>
</template>

<script lang="ts">
import {mapState, mapActions, mapGetters} from "vuex";
import store from "@/store";
import axios from "axios";

export default {
    name: "Header",
    props: {
        title: String,
        subtitle: String
    },
    computed: {
        ...mapState([
            "datasets",
            "activeDatasetId",
            "activeDataset",
            "loading",
            "labels"
        ]),
        ...mapGetters([
            "datasetType",
            "sampleShortTitle",
            "prevButtonDisabled",
            "nextButtonDisabled"
        ])
    },
    methods: {
        ...mapActions(["nextSample", "prevSample", "labelSample"]),
        route(toPath) {
            if (this.$route.path !== toPath) {
                this.$router.push(toPath);
            }
        },
        // temporary dummy login. Someone else, please create a login page!
        dummyLogin: function() {
            const tempApi = axios.create({
                baseURL: "http://127.0.0.1:5000/",
                withCredentials: false,
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json"
                }
            });
            tempApi
                .post("/login", {
                    username: "mario_nette",
                    password: "very_secret"
                })
                .then(function(result) {
                    console.log(result.data);
                    localStorage.setItem("jwtToken", result.data.access_token);
                    alert("Obtained JWT: " + localStorage.getItem("jwtToken"));
                });
        }
    },
    created(): void {
        this.$store.dispatch("loadAllDatasets");
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.sticky {
    position: fixed;
    top: 0;
    width: 100%;
}

.sticky + .section {
    padding-top: 3rem;
}
</style>
