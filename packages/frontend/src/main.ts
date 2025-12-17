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
  console.error('Vue Error:', err)
  console.error('Component:', instance)
  console.error('Info:', info)

  // 上报到 Sentry
  if (err instanceof Error) {
    captureException(err, { component: instance?.$options?.name, info })
  }
}

// 直接挂载应用，不进行复杂的初始化
try {
  console.log('🚀 挂载应用...')
  app.mount('#app')
  console.log('✅ 应用挂载成功')

  // 延迟初始化认证，避免阻塞应用启动
  setTimeout(async () => {
    try {
      console.log('🔐 开始初始化认证...')
      await tokenManager.initializeAuth()
      // 确保在Pinia完全初始化后再调用useAuthStore
      const { useAuthStore } = await import('./stores/modules/auth')
      const authStore = useAuthStore()
      await authStore.restoreFromStorage()
      console.log('✅ 认证初始化完成')
    } catch (error) {
      console.warn('⚠️ 认证初始化失败，但不影响应用使用:', error)
    }
  }, 500)

} catch (error) {
  console.error('❌ 应用挂载失败:', error)

  // 上报启动错误到 Sentry
  if (error instanceof Error) {
    captureException(error, { phase: 'app-mount' })
  }

  // 清除可能的问题数据
  try {
    localStorage.clear()
    app.mount('#app')
    console.log('✅ 应用重新挂载成功')
  } catch (retryError) {
    console.error('❌ 应用重新挂载也失败:', retryError)
    if (retryError instanceof Error) {
      captureException(retryError, { phase: 'app-mount-retry' })
    }
  }
}
