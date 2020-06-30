<template>
    <section class="section">
        <div class="container">
            <h1 class="title">Login</h1>

            <div class="box">
                <article class="media">
                    <div class="media-content">
                        <form @submit.prevent="submit">
                            <div class="field">
                                <label class="label">Username</label>
                                <div class="control has-icons-right">
                                    <input
                                        v-bind:class="{
                                            ['is-danger']:
                                                submitted && !username
                                        }"
                                        class="input"
                                        v-model="username"
                                        name="username"
                                        type="text"
                                        placeholder="Type your username"
                                    />
                                    <span class="icon is-small is-left">
                                        <i class="fas fa-user"></i>
                                    </span>
                                    <span class="icon is-small is-right">
                                        <i class="fas fa-check"></i>
                                    </span>
                                </div>
                                <p
                                    v-show="submitted && !username"
                                    class="help is-danger"
                                >
                                    Type your username
                                </p>
                            </div>
                            <div class="field">
                                <label class="label">Password</label>
                                <div class="control has-icons-right">
                                    <input
                                        v-bind:class="{
                                            ['is-danger']:
                                                submitted && !password
                                        }"
                                        v-model="password"
                                        class="input"
                                        name="password"
                                        type="password"
                                        placeholder="Type your password"
                                    />
                                    <span class="icon is-small is-left">
                                        <i class="fas fa-user"></i>
                                    </span>
                                    <span class="icon is-small is-right">
                                        <i class="fas fa-check"></i>
                                    </span>
                                </div>
                                <p
                                    v-if="submitted && !password"
                                    class="help is-danger"
                                >
                                    Type your password
                                </p>
                            </div>
                            <div class="field">
                                <div class="control">
                                    <button
                                        :disabled="status.loggingIn"
                                        class="button is-link"
                                    >
                                        Submit
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </article>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import Vue from "vue";
import {mapActions, mapState} from "vuex";

export default Vue.extend({
    name: "LOGIN",
    props: {},
    data: () => {
        const error = {username: false, password: false};
        return {
            username: "",
            password: "",
            submitted: false,
            error
        };
    },
    computed: {...mapState("login", ["status"])},
    created() {
        this.logout();
    },
    // mounted() {},
    methods: {
        ...mapActions("login", ["login", "logout"]),
        submit() {
            this.submitted = true;
            const {username, password} = this;
            if (username && password) {
                this.login({username, password});
            }
        }
    }
});
</script>

<style scoped lang="scss">
.container {
    margin: 10px auto;
    width: 50%;

    @media only screen and (max-width: 768px) {
        width: 90%;
    }

    .title {
        text-align: center;
    }
}
</style>
