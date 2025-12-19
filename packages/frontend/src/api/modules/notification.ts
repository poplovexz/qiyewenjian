/**
 * 通知管理API
 */
import { request } from '@/utils/request'

// 类型定义
interface NotificationListParams {
  page?: number
  size?: number
  tongzhi_zhuangtai?: string
  [key: string]: string | number | undefined
}

interface NotificationItem {
  id: string
  [key: string]: unknown
}

interface NotificationListResponse {
  items?: NotificationItem[]
  total?: number
}

export const notificationApi = {
  // 获取通知列表
  getList: (params: NotificationListParams) => {
    return request.get('/notifications', { params })
  },

  // 获取我的通知列表
  getMyList: (params: NotificationListParams) => {
    return request.get('/notifications/my', { params })
  },

  // 获取未读通知数量
  getUnreadCount: () => {
    return request.get('/notifications/my/unread-count')
  },

  // 根据ID获取通知详情
  getById: (id: string) => {
    return request.get(`/notifications/${id}`)
  },

  // 标记通知为已读
  markAsRead: (id: string) => {
    return request.post(`/notifications/${id}/read`)
  },

  // 批量标记为已读
  markMultipleAsRead: (ids: string[]) => {
    return Promise.all(ids.map((id) => request.post(`/notifications/${id}/read`)))
  },

  // 标记所有通知为已读
  markAllAsRead: () => {
    // 先获取所有未读通知，然后批量标记为已读
    return request
      .get('/notifications/my', {
        params: { tongzhi_zhuangtai: 'unread', size: 100 },
      })
      .then((response: NotificationListResponse) => {
        const unreadIds = response.items?.map((item: NotificationItem) => item.id) || []
        if (unreadIds.length > 0) {
          return notificationApi.markMultipleAsRead(unreadIds)
        }
        return Promise.resolve()
      })
  },
}
