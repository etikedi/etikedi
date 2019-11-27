import Vue from "vue";
import App from "./App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import "./registerServiceWorker";
import "@mdi/font/css/materialdesignicons.min.css";
Vue.config.productionTip = false;

Vue.use(Buefy, {
    defaultIconPack: "mdi",
});

new Vue({
  render: h => h(App)
}).$mount("#app");
