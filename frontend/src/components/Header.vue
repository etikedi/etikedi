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
                            <b-navbar-item href="#">
                                Label
                            </b-navbar-item>
                            <b-navbar-item href="#">
                                Upload
                            </b-navbar-item>
                            <b-navbar-item href="#">
                                Browse
                            </b-navbar-item>
                            <b-navbar-item class="remove-later">
                                <router-link to="/cifar">Cifar</router-link>
                            </b-navbar-item>
                            <b-navbar-item class="remove-later">
                                <router-link to="/dwtc">DWTC</router-link>
                            </b-navbar-item>
                            <b-navbar-item class="remove-later">
                                <router-link to="/equations"
                                    >Equations</router-link
                                >
                            </b-navbar-item>
                            <b-navbar-item class="remove-later">
                                <router-link to="/religious-texts"
                                    >Religious-Texts</router-link
                                >
                            </b-navbar-item>
                            <b-navbar-item class="remove-later">
                                <router-link to="/cv">CV</router-link>
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

            <div class="hero-foot" v-if="!isHomePage">
                <div class="container">
                    <div id="navbarMenuHeroA" class="navbar-menu">
                        <div class="navbar-start">
                            <b-button
                                class="navbar-item"
                                tag="a"
                                type="is-link"
                                icon-left="chevron-left"
                                @click="prevDataset"
                                :disabled="prevButtonDisabled"
                                inverted
                                outlined
                            >
                                Prev
                            </b-button>
                            <h2 class="title" style="padding: 0 1rem 0 1rem">
                                {{ $store.getters.activeDatasetId }}
                            </h2>
                            <b-button
                                class="navbar-item"
                                tag="a"
                                type="is-link"
                                icon-right="chevron-right"
                                @click="nextDataset"
                                :disabled="nextButtonDisabled"
                                inverted
                                outlined
                            >
                                Next
                            </b-button>
                        </div>
                        <div class="navbar-end">
                            <b-switch
                                class="navbar-item"
                                v-model="localDisplayFeatureTooltips"
                                type="is-warning"
                                v-if="localDisplayFeatureTooltipsSwitch"
                            >
                                Tooltips
                            </b-switch>
                            <b-button
                                v-for="(label, index) in labels"
                                :key="index"
                                class="navbar-item"
                                tag="a"
                                type="is-link"
                                @click="labelDataset(label)"
                                inverted
                                outlined
                            >
                                {{ label }}
                            </b-button>
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

export default {
    name: "Header",
    props: {
        title: String,
        subtitle: String
    },
    computed: {
        ...mapState(["prevButtonDisabled", "nextButtonDisabled"]),
        ...mapGetters(["labels"]),
        localDisplayFeatureTooltips: {
            get(): boolean {
                return store.state.displayFeatureTooltips;
            },
            set(newValue: boolean) {
                store.commit("toggleShowFeatureTooltips", newValue);
            }
        },
        localDisplayFeatureTooltipsSwitch: {
            get(): boolean {
                return store.state.displayFeatureTooltipsSwitch;
            }
        },
        isHomePage: {
            get(): boolean {
                return store.state.isHomePage;
            }
        }
    },
    methods: {
        ...mapActions(["nextDataset", "prevDataset", "labelDataset"])
    }
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
