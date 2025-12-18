import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// 引入Vant组件库
import Vant from 'vant'
import 'vant/lib/index.css'

// 引入权限指令
import { permission, role } from './directives/permission'





const app = createApp(App)

// 配置Pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(Vant)

// 注册全局指令
app.directive('permission', permission)
app.directive('role', role)



app.mount('#app')



