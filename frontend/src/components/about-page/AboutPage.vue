/* eslint-disable prettier/prettier */
<template>
    <div>
        <div class="para">
            <h1 class="tit">About AERGIA</h1>
            <hr class="intro" />

            <p class="intro">
                Aergia is an innovative labbelling tool powered by active
                learning. It allows you to label DWTC, CIFAR, equations as well
                as religious text. <br />
                The development of this tool started in the summer term of 2020
                as a practical course of the
                <a href="https://wwwdb.inf.tu-dresden.de/"
                    >chair of databases</a
                >
                at <a href="https://tu-dresden.de/">TU-Dresden</a>. The
                technology stack was set up by
                <a
                    href="https://wwwdb.inf.tu-dresden.de/our-group/team/julius-gonsior/"
                    >Julius Gonsior</a
                >, who also supervised the project. <br />
                In total 15 Students took part in this practical course. At the
                beginning the participants formed five groups. There was one
                large group, which was responible for the implementation of the
                backend and four additional groups, who were responible for
                developing the frontend for the different types of labeling.
            </p>
        </div>
    </div>
</template>

<script scoped lang="ts">
export default {
    name: "AboutPage",
    components: {}
};
</script>

<style lang="scss">
.tit {
    text-align: center;
    font-size: xxx-large;
}
</style>
