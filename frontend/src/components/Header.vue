<template>
    <header>
        <nav class="navbar hero is-primary is-bold is-fixed-top" role="navigation" aria-label="main navigation">
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
                            <b-button icon-left="chevron-left" @click="prevCv" :disabled=prevButtonDisabled>
                                Prev
                            </b-button>
                            <h2 class="title" style="padding: 0 1rem 0 1rem">{{ cv_id }}</h2>
                            <b-button icon-right="chevron-right" @click="nextCv" :disabled=nextButtonDisabled>
                                Next
                            </b-button>
                        </div>

                        <div class="navbar-end">
                            label 1 
                            label2
                            <a class="navbar-item is-active">
                                Home + {{ count }}
                            </a>
                            <a class="navbar-item">
                                Examples
                            </a>
                            <a class="navbar-item">
                                Documentation
                            </a>
                            <span class="navbar-item">
                                <a class="button is-primary is-inverted">
                                    <span class="icon">
                                        <i class="fab fa-github"></i>
                                    </span>
                                    <span>Download</span>
                                </a>
                            </span>
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
    computed:
        mapState(['cv_id', 'prevButtonDisabled', 'nextButtonDisabled']),
    methods:
        mapActions(['nextCv', 'prevCv']),
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
/*h3 {
    margin: 40px 0 0;
}*/
</style>
