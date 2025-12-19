import { createApp } from 'vue'
import './style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { tokenManager } from './utils/tokenManager'
import { initSentry, captureException } from './utils/sentry'

const app = createApp(App)

// 初始化 Sentry 错误监控（需要在其他插件之前初始化）
initSentry(app, router)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {

  // 上报到 Sentry
  if (err instanceof Error) {
    captureException(err, { component: instance?.$options?.name, info })
  }
}

// 直接挂载应用，不进行复杂的初始化
try {
  app.mount('#app')

  // 延迟初始化认证，避免阻塞应用启动
  setTimeout(async () => {
    try {
      await tokenManager.initializeAuth()
      // 确保在Pinia完全初始化后再调用useAuthStore
      const { useAuthStore } = await import('./stores/modules/auth')
      const authStore = useAuthStore()
      await authStore.restoreFromStorage()
    } catch (error) {
    }
  }, 500)
} catch (error) {

  // 上报启动错误到 Sentry
  if (error instanceof Error) {
    captureException(error, { phase: 'app-mount' })
  }

  // 清除可能的问题数据
  try {
    localStorage.clear()
    app.mount('#app')
  } catch (retryError) {
    if (retryError instanceof Error) {
      captureException(retryError, { phase: 'app-mount-retry' })
    }
  }
}
