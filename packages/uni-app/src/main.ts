import { createSSRApp } from "vue";
import { createPinia } from "pinia";
// @ts-ignore - uv-ui 没有类型声明
import uvUI from '@climblee/uv-ui';
import App from "./App.vue";
import { initSentry, captureException } from "./utils/sentry";

export function createApp() {
  const app = createSSRApp(App);
  const pinia = createPinia();

  // 初始化 Sentry 错误监控
  // 在生产环境配置 DSN: initSentry('your-sentry-dsn')
  initSentry();

  // 注册 Pinia
  app.use(pinia);

  // 注册 uv-ui 组件库
  app.use(uvUI);

  // 全局错误处理
  app.config.errorHandler = (err, instance, info) => {
    console.error('[Vue Error]', err);
    if (err instanceof Error) {
      captureException(err, { component: instance?.$options?.name, info });
    }
  };

  return {
    app,
  };
}
