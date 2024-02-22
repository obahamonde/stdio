import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router/auto";
import App from "./App.vue";
import { Icon } from "@iconify/vue";
import { createPinia } from "pinia";

import "@unocss/reset/tailwind.css";
import "./styles/main.scss";
import "uno.css";

const app = createApp(App);
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
});
app.use(router);
app.use(createPinia());
app.component("Icon", Icon);
app.mount("#app");
