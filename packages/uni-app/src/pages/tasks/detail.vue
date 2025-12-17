<template>
  <view class="detail-container">
    <view v-if="loading" class="loading-container">
      <text>加载中...</text>
    </view>

    <template v-else>
      <view class="detail-card">
        <view class="card-header">
          <text class="title">{{ task.chanpin_mingcheng || task.buzou_mingcheng || '任务项' }}</text>
          <text class="status" :class="task.xiangmu_zhuangtai">{{ getStatusText(task.xiangmu_zhuangtai) }}</text>
        </view>

        <view class="info-list">
          <view class="info-item">
            <text class="label">客户名称</text>
            <text class="value">{{ task.kehu_mingcheng || '未知' }}</text>
          </view>
          <view class="info-item">
            <text class="label">工单编号</text>
            <text class="value">{{ task.gongdan_bianhao || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="label">计划工时</text>
            <text class="value">{{ task.jihua_gongshi || 0 }} 小时</text>
          </view>
          <view v-if="task.shiji_gongshi" class="info-item">
            <text class="label">实际工时</text>
            <text class="value">{{ task.shiji_gongshi }} 小时</text>
          </view>
          <view v-if="task.kaishi_shijian" class="info-item">
            <text class="label">开始时间</text>
            <text class="value">{{ formatDate(task.kaishi_shijian) }}</text>
          </view>
          <view v-if="task.jieshu_shijian" class="info-item">
            <text class="label">完成时间</text>
            <text class="value">{{ formatDate(task.jieshu_shijian) }}</text>
          </view>
          <view v-if="task.beizhu" class="info-item">
            <text class="label">备注</text>
            <text class="value">{{ task.beizhu }}</text>
          </view>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view class="action-bar">
        <button v-if="task.xiangmu_zhuangtai === 'pending'" class="btn primary" :loading="submitting" @click="handleStartTask">
          开始任务
        </button>
        <button v-if="task.xiangmu_zhuangtai === 'in_progress'" class="btn success" :loading="submitting" @click="showCompleteModal">
          完成任务
        </button>
        <button v-if="task.xiangmu_zhuangtai === 'in_progress'" class="btn warning" :loading="submitting" @click="handlePauseTask">
          暂停任务
        </button>
      </view>
    </template>

    <!-- 完成任务弹窗 -->
    <uv-popup v-model="completeModalVisible" mode="bottom" round="16" :safeAreaInsetBottom="true">
      <view class="complete-modal">
        <view class="modal-title">完成任务</view>
        <view class="modal-form">
          <view class="form-item">
            <text class="form-label">实际工时（小时）</text>
            <uv-input v-model="completeForm.shiji_gongshi" type="number" placeholder="请输入实际工时" />
          </view>
          <view class="form-item">
            <text class="form-label">备注说明</text>
            <uv-textarea v-model="completeForm.beizhu" placeholder="请输入备注（选填）" :maxlength="500" />
          </view>
        </view>
        <view class="modal-actions">
          <button class="btn default" @click="completeModalVisible = false">取消</button>
          <button class="btn success" :loading="submitting" @click="handleCompleteTask">确认完成</button>
        </view>
      </view>
    </uv-popup>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getTaskDetail, startTask, completeTask, pauseTask } from '@/api/task'
import { TASK_STATUS_MAP } from '@/constants'
import dayjs from 'dayjs'

interface TaskDetail {
  id: string
  chanpin_mingcheng?: string
  buzou_mingcheng?: string
  kehu_mingcheng?: string
  gongdan_bianhao?: string
  xiangmu_zhuangtai: string
  jihua_gongshi?: number
  shiji_gongshi?: number
  kaishi_shijian?: string
  jieshu_shijian?: string
  beizhu?: string
}

const taskId = ref('')
const loading = ref(true)
const submitting = ref(false)
const completeModalVisible = ref(false)

const task = ref<TaskDetail>({
  id: '',
  xiangmu_zhuangtai: 'pending'
})

const completeForm = reactive({
  shiji_gongshi: '',
  beizhu: ''
})

const getStatusText = (status: string) => TASK_STATUS_MAP[status]?.label || status

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

// 加载任务详情
const loadTaskDetail = async () => {
  loading.value = true
  try {
    const data = await getTaskDetail(taskId.value)
    task.value = data
  } catch (error) {
    console.error('加载任务详情失败:', error)
    // 开发环境 Mock 数据
    if (import.meta.env.DEV) {
      task.value = {
        id: taskId.value,
        chanpin_mingcheng: '月度记账服务',
        kehu_mingcheng: '张三公司',
        gongdan_bianhao: 'GD202412001',
        xiangmu_zhuangtai: 'pending',
        jihua_gongshi: 2,
        beizhu: '为客户提供月度记账服务，包括凭证录入、账簿登记等工作。'
      }
    } else {
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  } finally {
    loading.value = false
  }
}

// 开始任务
const handleStartTask = async () => {
  submitting.value = true
  try {
    await startTask(taskId.value)
    task.value.xiangmu_zhuangtai = 'in_progress'
    task.value.kaishi_shijian = new Date().toISOString()
    uni.showToast({ title: '任务已开始', icon: 'success' })
  } catch (error: any) {
    // 开发环境 Mock
    if (import.meta.env.DEV) {
      task.value.xiangmu_zhuangtai = 'in_progress'
      task.value.kaishi_shijian = new Date().toISOString()
      uni.showToast({ title: '任务已开始', icon: 'success' })
    } else {
      uni.showToast({ title: error.message || '操作失败', icon: 'none' })
    }
  } finally {
    submitting.value = false
  }
}

// 显示完成弹窗
const showCompleteModal = () => {
  completeForm.shiji_gongshi = String(task.value.jihua_gongshi || '')
  completeForm.beizhu = ''
  completeModalVisible.value = true
}

// 完成任务
const handleCompleteTask = async () => {
  if (!completeForm.shiji_gongshi) {
    uni.showToast({ title: '请输入实际工时', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await completeTask(taskId.value, {
      shiji_gongshi: Number(completeForm.shiji_gongshi),
      beizhu: completeForm.beizhu
    })
    task.value.xiangmu_zhuangtai = 'completed'
    task.value.shiji_gongshi = Number(completeForm.shiji_gongshi)
    task.value.jieshu_shijian = new Date().toISOString()
    completeModalVisible.value = false
    uni.showToast({ title: '任务已完成', icon: 'success' })
  } catch (error: any) {
    // 开发环境 Mock
    if (import.meta.env.DEV) {
      task.value.xiangmu_zhuangtai = 'completed'
      task.value.shiji_gongshi = Number(completeForm.shiji_gongshi)
      task.value.jieshu_shijian = new Date().toISOString()
      completeModalVisible.value = false
      uni.showToast({ title: '任务已完成', icon: 'success' })
    } else {
      uni.showToast({ title: error.message || '操作失败', icon: 'none' })
    }
  } finally {
    submitting.value = false
  }
}

// 暂停任务
const handlePauseTask = async () => {
  uni.showModal({
    title: '提示',
    content: '确定要暂停此任务吗？',
    success: async (res) => {
      if (res.confirm) {
        submitting.value = true
        try {
          await pauseTask(taskId.value)
          task.value.xiangmu_zhuangtai = 'pending'
          uni.showToast({ title: '任务已暂停', icon: 'success' })
        } catch (error: any) {
          if (import.meta.env.DEV) {
            task.value.xiangmu_zhuangtai = 'pending'
            uni.showToast({ title: '任务已暂停', icon: 'success' })
          } else {
            uni.showToast({ title: error.message || '操作失败', icon: 'none' })
          }
        } finally {
          submitting.value = false
        }
      }
    }
  })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  taskId.value = (currentPage as any).options?.id || ''

  if (taskId.value) {
    loadTaskDetail()
  } else {
    uni.showToast({ title: '任务ID不存在', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1500)
  }
})
</script>

<style lang="scss" scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx;
  padding-bottom: 200rpx;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
  color: #999;
  font-size: 28rpx;
}

.detail-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 30rpx;
    border-bottom: 1rpx solid #eee;

    .title {
      font-size: 36rpx;
      font-weight: bold;
      color: #333;
      flex: 1;
    }

    .status {
      font-size: 24rpx;
      padding: 8rpx 16rpx;
      border-radius: 8rpx;
      margin-left: 16rpx;

      &.pending { background: #fff7e6; color: #fa8c16; }
      &.in_progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
      &.skipped { background: #f5f5f5; color: #999; }
    }
  }

  .info-list {
    padding-top: 30rpx;

    .info-item {
      display: flex;
      margin-bottom: 30rpx;

      .label {
        width: 160rpx;
        font-size: 28rpx;
        color: #999;
        flex-shrink: 0;
      }

      .value {
        flex: 1;
        font-size: 28rpx;
        color: #333;
      }
    }
  }
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 20rpx;

  .btn {
    flex: 1;
    height: 90rpx;
    border-radius: 10rpx;
    font-size: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;

    &.primary { background: #1989fa; color: #fff; }
    &.success { background: #07c160; color: #fff; }
    &.warning { background: #ff9800; color: #fff; }
    &.default { background: #f5f5f5; color: #666; }
  }
}

.complete-modal {
  padding: 30rpx;

  .modal-title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
    text-align: center;
    margin-bottom: 40rpx;
  }

  .modal-form {
    .form-item {
      margin-bottom: 30rpx;

      .form-label {
        font-size: 28rpx;
        color: #666;
        margin-bottom: 16rpx;
        display: block;
      }
    }
  }

  .modal-actions {
    display: flex;
    gap: 20rpx;
    margin-top: 40rpx;

    .btn {
      flex: 1;
      height: 90rpx;
      border-radius: 10rpx;
      font-size: 32rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      border: none;

      &.default { background: #f5f5f5; color: #666; }
      &.success { background: #07c160; color: #fff; }
    }
  }
}
</style>

