<template>
  <el-popover
    :width="400"
    trigger="click"
    placement="bottom-end"
    popper-class="notification-popover"
    @show="handleShow"
  >
    <template #reference>
      <button class="action-btn notification-btn" title="通知">
        <el-icon><Bell /></el-icon>
        <div v-if="notificationStore.hasUnread" class="notification-badge">
          {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
        </div>
      </button>
    </template>

    <div class="notification-center">
      <!-- 头部 -->
      <div class="notification-header">
        <h3>通知中心</h3>
        <el-button
          v-if="notificationStore.hasUnread"
          link
          type="primary"
          size="small"
          @click="handleMarkAllAsRead"
        >
          全部已读
        </el-button>
      </div>

      <!-- 通知列表 -->
      <div v-loading="notificationStore.loading" class="notification-list">
        <template v-if="notificationStore.notifications.length > 0">
          <div
            v-for="notification in notificationStore.notifications"
            :key="notification.id"
            class="notification-item"
            :class="{ 'is-unread': notification.tongzhi_zhuangtai === 'unread' }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon" :class="`type-${notification.tongzhi_leixing}`">
              <el-icon>
                <component :is="getNotificationIcon(notification.tongzhi_leixing)" />
              </el-icon>
            </div>
            <div class="notification-content">
              <div class="notification-title">{{ notification.tongzhi_biaoti }}</div>
              <div class="notification-desc">{{ getNotificationDesc(notification.tongzhi_neirong) }}</div>
              <div class="notification-time">{{ formatTime(notification.fasong_shijian) }}</div>
            </div>
            <div v-if="notification.tongzhi_zhuangtai === 'unread'" class="unread-dot"></div>
          </div>
        </template>
        <el-empty v-else description="暂无通知" :image-size="80" />
      </div>

      <!-- 底部 -->
      <div class="notification-footer">
        <el-button link type="primary" @click="handleViewAll">
          查看全部通知
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Warning, SuccessFilled, CircleCheck, Document } from '@element-plus/icons-vue'
import { useNotificationStore } from '@/stores/modules/notification'
import { ElMessage } from 'element-plus'

// 通知类型
interface Notification {
  id: string
  tongzhi_zhuangtai: string
  lianjie_url?: string
  tongzhi_leixing?: string
  tongzhi_neirong?: string
  chuangjian_shijian?: string
}

const router = useRouter()
const notificationStore = useNotificationStore()

// 获取通知图标
const getNotificationIcon = (type: string) => {
  const iconMap: Record<string, Component> = {
    'audit_pending': Warning,
    'audit_approved': SuccessFilled,
    'audit_rejected': Warning,
    'payment_success': CircleCheck,
    'payment_failed': Warning,
    'contract_signed': Document,
    'invoice_generated': Document,
    'task_assigned': Document
  }
  return iconMap[type] || Bell
}

// 获取通知描述（截取前50个字符）
const getNotificationDesc = (content: string) => {
  if (!content) return ''
  const lines = content.split('\n').filter(line => line.trim())
  const firstLine = lines[0] || ''
  return firstLine.length > 50 ? firstLine.substring(0, 50) + '...' : firstLine
}

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  
  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < 7 * day) {
    return `${Math.floor(diff / day)}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

// 显示通知面板时刷新数据
const handleShow = async () => {
  await notificationStore.fetchNotifications({ page: 1, size: 10 })
}

// 点击通知
const handleNotificationClick = async (notification: Notification) => {
  // 标记为已读
  if (notification.tongzhi_zhuangtai === 'unread') {
    await notificationStore.markAsRead(notification.id)
  }

  // 跳转到相关页面
  if (notification.lianjie_url) {
    router.push(notification.lianjie_url)
  }
}

// 标记所有为已读
const handleMarkAllAsRead = async () => {
  await notificationStore.markAllAsRead()
}

// 查看全部通知
const handleViewAll = () => {
  router.push('/notifications')
}

// 组件挂载时启动自动刷新
onMounted(() => {
  notificationStore.startAutoRefresh(30000) // 每30秒刷新一次
})

// 组件卸载时停止自动刷新
onUnmounted(() => {
  notificationStore.stopAutoRefresh()
})
</script>

<style scoped lang="scss">
.notification-btn {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: #f56c6c;
  color: white;
  border-radius: 9px;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 0 0 2px var(--el-bg-color);
}

.notification-center {
  display: flex;
  flex-direction: column;
  max-height: 500px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--el-border-color-lighter);
  
  &:hover {
    background-color: var(--el-fill-color-light);
  }
  
  &.is-unread {
    background-color: var(--el-color-primary-light-9);
  }
}

.notification-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 18px;
  
  &.type-audit_pending {
    background-color: var(--el-color-warning-light-9);
    color: var(--el-color-warning);
  }
  
  &.type-audit_approved {
    background-color: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }
  
  &.type-audit_rejected {
    background-color: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }
  
  &.type-payment_success {
    background-color: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }
  
  &.type-payment_failed {
    background-color: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.unread-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  background-color: var(--el-color-primary);
  border-radius: 50%;
  margin-top: 14px;
}

.notification-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  text-align: center;
}
</style>

<style lang="scss">
.notification-popover {
  padding: 0 !important;
}
</style>
