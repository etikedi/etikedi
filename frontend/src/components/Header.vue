<template>
    <header>
        <nav class="navbar is-fixed-top hero is-info is-bold" role="navigation" aria-label="main navigation">
            <div class="hero-head">
                <div class="container">
                    <div class="navbar-menu">
                        <div class="navbar-end">
                            <a class="navbar-item is-active" @click="nextCv">
                                Home
                            </a>
                            <a class="navbar-item">
                                Examples
                            </a>
                            <a class="navbar-item">
                                Documentation
                            </a>

                        </div>
                    </div>
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

            <div class="hero-foot">
                <div class="container">
                    <div id="navbarMenuHeroA" class="navbar-menu">
                        <div class="navbar-start">
                            <b-button class="navbar-item" tag="a" type="is-link" icon-left="chevron-left"
                                      @click="prevCv" :disabled=prevButtonDisabled inverted outlined>
                                Prev
                            </b-button>
                            <h2 class="title" style="padding: 0 1rem 0 1rem">{{ cvId }}</h2>
                            <b-button class="navbar-item" tag="a" type="is-link" icon-right="chevron-right"
                                      @click="nextCv" :disabled=nextButtonDisabled inverted outlined>
                                Next
                            </b-button>
                        </div>
                        <b-select v-model="objectType" placeholder="Objekttyp auswählen">
                            <option value="1">CIFAR</option>
                            <option value="2">DWTC</option>
                            <option value="3">Equations</option>
                            <option value="4">Religious Texts</option>
                            <option value="5">Resumees</option>
                        </b-select>

                        <div class="navbar-end">
                            <b-switch
                                    class="navbar-item"
                                    v-model="localDisplayFeatureTooltips"
                                    type="is-warning"> Tooltips
                            </b-switch>
                            <b-button v-for="(label,index) in labels" :key="index" class="navbar-item" tag="a"
                                      type="is-link" @click="labelThis(label)" inverted outlined>
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
    import {mapState, mapActions, mapGetters} from 'vuex';
    import store from "@/store";

    export default {
        name: "Header",
        props: {
            title: String,
            subtitle: String
        },
        data: function () {
            return {
                objectType: null,
                labels: ['skill', 'noskill']
            }
        },
        computed: {
            ...mapState(['cvId', 'prevButtonDisabled', 'nextButtonDisabled']),
            localDisplayFeatureTooltips: {
                get(): boolean {

                    return store.state.displayFeatureTooltips;
                },
                set(newValue: boolean) {
                    store.commit("toggleShowFeatureTooltips", newValue);
                }
            }
        },
        methods:{
            ...mapActions(['nextCv', 'prevCv', 'labelThis'])
            
        },
        handleHeaderScroll(event: Event) {
                window.console.log("oh oh");
                // don't know where function 'error(string)' is declared, neither what it's supposed to do so replaced it with 'alert("ui")'
                // error("ui");
                alert("ui")
        },
        created() {
                window.addEventListener('scroll', this.handleHeaderScroll);
        },
        destroyed() {
                window.removeEventListener('scroll', this.handleHeaderScroll);
        },
        watch:{
            objectType: function(value){
                this.$emit("updateObjectType", value);
            }
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
