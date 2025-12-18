/**
 * 通知管理Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '@/api/modules/notification'
import { ElMessage } from 'element-plus'

export const useNotificationStore = defineStore('notification', () => {
  // 状态
  const notifications = ref<any[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const total = ref(0)

  // 计算属性
  const hasUnread = computed(() => unreadCount.value > 0)
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => n.tongzhi_zhuangtai === 'unread')
  )

  // 获取未读通知数量
  const fetchUnreadCount = async () => {
    try {
      const response = await notificationApi.getUnreadCount()
      unreadCount.value = response.unread_count || 0
      return unreadCount.value
    } catch (error) {
      console.error('获取未读通知数量失败:', error)
      return 0
    }
  }

  // 获取通知列表（当前用户的通知）
  const fetchNotifications = async (params: any = {}) => {
    try {
      loading.value = true
      const response = await notificationApi.getMyList(params)
      notifications.value = response.items || []
      total.value = response.total || 0
      return response
    } catch (error) {
      console.error('获取通知列表失败:', error)
      ElMessage.error('获取通知列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 标记通知为已读
  const markAsRead = async (id: string) => {
    try {
      await notificationApi.markAsRead(id)
      
      // 更新本地状态
      const notification = notifications.value.find(n => n.id === id)
      if (notification && notification.tongzhi_zhuangtai === 'unread') {
        notification.tongzhi_zhuangtai = 'read'
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      
      return true
    } catch (error) {
      console.error('标记通知为已读失败:', error)
      ElMessage.error('标记通知为已读失败')
      return false
    }
  }

  // 标记所有通知为已读
  const markAllAsRead = async () => {
    try {
      loading.value = true
      await notificationApi.markAllAsRead()
      
      // 更新本地状态
      notifications.value.forEach(n => {
        if (n.tongzhi_zhuangtai === 'unread') {
          n.tongzhi_zhuangtai = 'read'
        }
      })
      unreadCount.value = 0
      
      ElMessage.success('已标记所有通知为已读')
      return true
    } catch (error) {
      console.error('标记所有通知为已读失败:', error)
      ElMessage.error('标记所有通知为已读失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 定时刷新未读数量
  let refreshTimer: any = null
  const startAutoRefresh = (interval = 30000) => {
    stopAutoRefresh()
    fetchUnreadCount() // 立即执行一次
    refreshTimer = setInterval(() => {
      fetchUnreadCount()
    }, interval)
  }

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  return {
    // 状态
    notifications,
    unreadCount,
    loading,
    total,
    
    // 计算属性
    hasUnread,
    unreadNotifications,
    
    // 方法
    fetchUnreadCount,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    startAutoRefresh,
    stopAutoRefresh
  }
})

