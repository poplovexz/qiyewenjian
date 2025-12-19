<template>
  <div class="notification-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通知偏好</span>
        </div>
      </template>

      <el-alert
        title="通知说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        您可以选择接收哪些类型的通知。关闭某项通知后，您将不会收到该类型的提醒。
      </el-alert>

      <div class="notification-items">
        <div class="notification-item">
          <div class="item-info">
            <div class="item-title">
              <el-icon><Message /></el-icon>
              <span>邮件通知</span>
            </div>
            <div class="item-desc">
              接收系统发送的邮件通知，包括重要事项提醒、审核通知等
            </div>
          </div>
          <el-switch
            v-model="preferences.email_notification"
            @change="handleChange"
            :loading="loading"
          />
        </div>

        <el-divider />

        <div class="notification-item">
          <div class="item-info">
            <div class="item-title">
              <el-icon><ChatDotRound /></el-icon>
              <span>短信通知</span>
            </div>
            <div class="item-desc">
              接收系统发送的短信通知，用于紧急事项提醒
            </div>
          </div>
          <el-switch
            v-model="preferences.sms_notification"
            @change="handleChange"
            :loading="loading"
          />
        </div>

        <el-divider />

        <div class="notification-item">
          <div class="item-info">
            <div class="item-title">
              <el-icon><Bell /></el-icon>
              <span>系统消息</span>
            </div>
            <div class="item-desc">
              接收系统内的消息通知，在系统内显示通知提醒
            </div>
          </div>
          <el-switch
            v-model="preferences.system_notification"
            @change="handleChange"
            :loading="loading"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Message, ChatDotRound, Bell } from '@element-plus/icons-vue'
import { getUserPreferences, updateUserPreferences, type UserPreferences } from '@/api/modules/settings'

const loading = ref(false)

// 通知偏好设置
const preferences = reactive<UserPreferences>({
  email_notification: true,
  sms_notification: true,
  system_notification: true
})

// 加载偏好设置
const loadPreferences = async () => {
  try {
    const data = await getUserPreferences()
    preferences.email_notification = data.email_notification
    preferences.sms_notification = data.sms_notification
    preferences.system_notification = data.system_notification
  } catch (error) {
    ElMessage.error('加载通知偏好失败')
  }
}

// 处理设置变更
const handleChange = async () => {
  loading.value = true
  try {
    await updateUserPreferences({
      email_notification: preferences.email_notification,
      sms_notification: preferences.sms_notification,
      system_notification: preferences.system_notification
    })
    ElMessage.success('设置已保存')
  } catch (error: unknown) {
    const err = error as { message?: string }
    ElMessage.error(err.message || '保存失败')
    // 失败时重新加载设置
    await loadPreferences()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPreferences()
})
</script>

<style scoped lang="scss">
.notification-settings {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .notification-items {
    .notification-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 0;

      .item-info {
        flex: 1;

        .item-title {
          display: flex;
          align-items: center;
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 8px;

          .el-icon {
            margin-right: 8px;
            font-size: 18px;
          }
        }

        .item-desc {
          font-size: 14px;
          color: #909399;
          line-height: 1.5;
        }
      }
    }
  }
}
</style>
