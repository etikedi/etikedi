<template>
    <section class="section">
        <div class="container">
            <h1 class="title">{{ cv_id }}</h1>
            <b-button icon-left="chevron-left" @click="loadPrevCv" :disabled=prevButtonDisabled>
                Prev
            </b-button>
            <b-button icon-right="chevron-right" @click="loadNextCv" :disabled=nevtButtonDisable>
                Next
            </b-button>
            <pre>
                {{ cv.content }}
            </pre>
            <p>
                {{ cv.label }}
            </p>
        </div>
    </section>
</template>

<script>
export default {
    name: "CV",
    props: {},
    data() {
        return {
            cv_id: 5,
            cv: {
                content: "Loading CV…",
                label: ""
            },
            prevButtonDisabled: false,
            nevtButtonDisable: false
        }
    },
    mounted() {
        this.fetchCv().catch(error => {
            console.error(error);
        });
    },
    /*created: function() {
        this.loadCv(this.cv_id);
    },*/
    methods: {
        async fetchCv() {
            this.cv = await fetch('http://127.0.0.1:5000/api/resumees/' + this.cv_id)
                .then(result => result.json())
                .catch(function (error) {
                    this.cv.content= "Error! Could not reach the API. " + error
                });
        },
        loadNextCv() {
            if (this.cv_id == 1)
                this.prevButtonDisabled = false
            this.cv_id += 1;
        },
        loadPrevCv() {
            if (this.cv_id == 2) {
                this.prevButtonDisabled = true;
                this.cv_id -= 1;
            } else {
                this.cv_id -= 1;
            }
        }
    },
    watch: {
        cv_id: {
            handler: function() {
                this.fetchCv().catch(error => {
                    console.error(error)
                })
            }
        }
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
