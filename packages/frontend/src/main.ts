import { createApp } from 'vue'
import './style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { useAuthStore } from './stores/modules/auth'
import { tokenManager } from './utils/tokenManager'

const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

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
      const authStore = useAuthStore()
      await authStore.restoreFromStorage()
      console.log('✅ 认证初始化完成')
    } catch (error) {
      console.warn('⚠️ 认证初始化失败，但不影响应用使用:', error)
    }
  }, 500)

} catch (error) {
  console.error('❌ 应用挂载失败:', error)
  // 清除可能的问题数据
  try {
    localStorage.clear()
    app.mount('#app')
    console.log('✅ 应用重新挂载成功')
  } catch (retryError) {
    console.error('❌ 应用重新挂载也失败:', retryError)
  }
}
