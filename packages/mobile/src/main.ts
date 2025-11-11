import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// 引入Vant组件库
import Vant from 'vant'
import 'vant/lib/index.css'

console.log('🚀 移动端应用开始初始化...')
console.log('📍 当前路径:', window.location.pathname)
console.log('🔗 Base URL:', import.meta.env.BASE_URL)

const app = createApp(App)

// 配置Pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(Vant)

console.log('✅ 插件已加载，准备挂载应用...')

app.mount('#app')

console.log('✅ 应用已挂载到 #app')

