import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([])
  const loading = ref(false)

  const fetchUsers = async () => {
    loading.value = true
    try {
      // 这里将来会调用 API
      console.log('获取用户列表')
      
      // 模拟数据
      users.value = [
        { id: '1', email: 'admin@example.com', name: '管理员', role: 'admin' },
        { id: '2', email: 'accountant@example.com', name: '会计', role: 'accountant' },
        { id: '3', email: 'customer@example.com', name: '客户', role: 'customer' },
      ]
    } catch (error) {
      console.error('获取用户列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    users,
    loading,
    fetchUsers,
  }
})
