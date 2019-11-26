<template>
    <div class="container">
        <h1 class="title">{{ msg }}</h1>
        <p class="subtitle">
            {{ content }}
        </p>
    </div>
</template>

<script>
export default {
    name: "HelloWorld",
    props: {
        msg: String,
        content: String
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
/*h3 {
    margin: 40px 0 0;
}*/
</style>
