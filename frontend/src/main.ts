import Vue from "vue";
import App from "./App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import "./registerServiceWorker";
import "@mdi/font/css/materialdesignicons.min.css";
import store from "./store"

Vue.config.productionTip = false;

Vue.use(Buefy, {
    defaultIconPack: "mdi",
});

new Vue({
    store,
    el: '#app',
    render: h => h(App),
});

