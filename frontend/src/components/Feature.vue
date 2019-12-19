<template>
    <span 
            v-html="text" 
            style="border: 1px darkgrey dashed;"
            :class="label" />
</template>

<script>
export default {
    name: "Feature",
    props: {
        text: String, 
        label: String
    },
};
</script>

<style scoped lang="scss">
.skill {
    color: red;
}

.noskill {
    color: blue;
}
</style>
