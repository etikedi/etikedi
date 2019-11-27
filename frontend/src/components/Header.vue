<template>
    <section class = "hero is-primary is-bold">
        <div class="hero-body">
            <div class="container">
                <h1 class="title">{{ title }}</h1>
                <p class="subtitle">
                    {{ subtitle }}
                </p>
            </div>
        </div>
    </section>
</template>

<script>
export default {
    name: "Header",
    props: {
        title: String,
        subtitle: String
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
/*h3 {
margin: 40px 0 0;
}*/
</style>
