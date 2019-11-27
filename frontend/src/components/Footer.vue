<template>
    <footer class="footer">
        <div class="content has-text-centered">
            <p>
                <strong>{{ title }}</strong> by <a :href="homepage">{{ author }}</a>. The source code is licensed
                <a href="http://opensource.org/licenses/mit-license.php">MIT</a>. The websites content is licensed <a href="http://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY NC SA 4.0</a>.
            </p>
        </div>
    </footer>
</template>

<script>
export default {
    name: "Footer",
    props: {
        title: String,
        homepage: String,
        author: String
    }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
/*h3 {
margin: 40px 0 0;
}*/
</style>
