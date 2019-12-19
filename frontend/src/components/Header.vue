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
                            <b-button class="navbar-item" tag="a" type="is-link" icon-left="chevron-left" @click="prevCv" :disabled=prevButtonDisabled inverted outlined>
                                Prev
                            </b-button>
                            <h2 class="title" style="padding: 0 1rem 0 1rem">{{ cv_id }}</h2>
                            <b-button class="navbar-item" tag="a" type="is-link" icon-right="chevron-right" @click="nextCv" :disabled=nextButtonDisabled inverted outlined>
                                Next
                            </b-button>
                        </div>
                        <div class="navbar-end">
                            <b-button v-for="(label,index) in labels" :key="index" class="navbar-item" tag="a" type="is-link" @click="labelThis(label)" inverted outlined>
                                {{ label }}
                            </b-button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    </header>
</template>

<script>

import { mapState, mapActions } from 'vuex';

export default {
    name: "Header",
    props: {
        title: String,
        subtitle: String
    },
    data: function () {
        return {
            labels: ['skill', 'noskill']
        }
    },
    computed: 
    mapState(['cv_id', 'prevButtonDisabled', 'nextButtonDisabled'])
    ,
    methods: 
    mapActions(['nextCv', 'prevCv', 'labelThis']),
    handleHeaderScroll(event) {
        window.console.log("oh oh");
        error("ui");
    },
    created () {
        window.addEventListener('scroll', this.handleHeaderScroll);
    },
    destroyed () {
        window.removeEventListener('scroll', this.handleHeaderScroll);
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
