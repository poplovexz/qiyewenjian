import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserInfo {
  id: string
  yonghu_ming: string
  xingming: string
  youxiang?: string
  shouji?: string
}

export const useUserStore = defineStore(
  'user',
  () => {
    const token = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)

    // 设置Token
    function setToken(newToken: string) {
      token.value = newToken
    }

    // 设置用户信息
    function setUserInfo(info: UserInfo) {
      userInfo.value = info
    }

    // 清除用户信息
    function clearUserInfo() {
      token.value = ''
      userInfo.value = null
    }

    // 登录
    async function login(username: string, password: string) {
      // 这里会在后面实现API调用
      console.log('Login:', username, password)
    }

    // 退出登录
    function logout() {
      clearUserInfo()
    }

    return {
      token,
      userInfo,
      setToken,
      setUserInfo,
      clearUserInfo,
      login,
      logout
    }
  },
  {
    persist: true // 持久化存储
  }
)

