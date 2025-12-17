import { createSSRApp } from "vue";
import { createPinia } from "pinia";
import uvUI from '@climblee/uv-ui';
import App from "./App.vue";

export function createApp() {
  const app = createSSRApp(App);
  const pinia = createPinia();

  // 注册 Pinia
  app.use(pinia);

  // 注册 uv-ui 组件库
  app.use(uvUI);

  return {
    app,
  };
}
