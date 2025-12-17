<template>
  <div class="task-detail-container">
    <van-nav-bar title="任务详情" left-arrow @click-left="router.back()" fixed placeholder />

    <div v-if="task" class="task-content">
      <van-cell-group inset title="基本信息">
        <van-cell title="任务名称" :value="task.renwu_mingcheng" />
        <van-cell title="任务状态">
          <template #value>
            <van-tag :type="getStatusType(task.xiangmu_zhuangtai)">
              {{ getStatusText(task.xiangmu_zhuangtai) }}
            </van-tag>
          </template>
        </van-cell>
        <van-cell title="工单编号" :value="task.gongdan.gongdan_bianhao" />
        <van-cell title="客户名称" :value="task.kehu?.kehu_mingcheng || '-'" />
        <van-cell title="计划工时" :value="`${task.jihua_gongshi}小时`" />
        <van-cell v-if="task.shiji_gongshi" title="实际工时" :value="`${task.shiji_gongshi}小时`" />
      </van-cell-group>

      <van-cell-group v-if="task.renwu_miaoshu" inset title="任务描述">
        <van-cell>
          <div class="task-description">{{ task.renwu_miaoshu }}</div>
        </van-cell>
      </van-cell-group>

      <div class="action-buttons">
        <van-button
          v-if="task.xiangmu_zhuangtai === 'pending'"
          type="primary"
          block
          @click="handleStart"
        >
          开始任务
        </van-button>

        <van-button
          v-if="task.xiangmu_zhuangtai === 'in_progress'"
          type="success"
          block
          @click="showCompleteDialog = true"
        >
          完成任务
        </van-button>

        <van-button
          v-if="task.xiangmu_zhuangtai === 'in_progress'"
          type="warning"
          block
          @click="handlePause"
        >
          暂停任务
        </van-button>
      </div>
    </div>

    <!-- 完成任务对话框 -->
    <van-dialog
      v-model:show="showCompleteDialog"
      title="完成任务"
      show-cancel-button
      @confirm="handleComplete"
    >
      <van-field
        v-model="actualHours"
        type="number"
        label="实际工时"
        placeholder="请输入实际工时（小时）"
        :rules="[{ required: true, message: '请输入实际工时' }]"
      />
      <van-field
        v-model="completeRemark"
        type="textarea"
        label="备注"
        placeholder="请输入备注（可选）"
        rows="3"
      />
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { getMyTaskItems, startTaskItem, completeTaskItem, pauseTaskItem } from '@/api/task'
import type { TaskItem, TaskItemStatus } from '@/types/task'

const router = useRouter()
const route = useRoute()

const task = ref<TaskItem | null>(null)
const showCompleteDialog = ref(false)
const actualHours = ref('')
const completeRemark = ref('')

const loadTask = async () => {
  try {
    const taskId = route.params.id as string
    const res = await getMyTaskItems({ page: 1, size: 100 })
    task.value = res.items.find(item => item.id === taskId) || null
  } catch (error) {
    console.error('Load task error:', error)
  }
}

const handleStart = async () => {
  try {
    await showConfirmDialog({
      title: '确认',
      message: '确定要开始这个任务吗？'
    })

    await startTaskItem(task.value!.id)
    showToast({ message: '任务已开始', type: 'success' })
    await loadTask()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Start task error:', error)
    }
  }
}

const handleComplete = async () => {
  try {
    if (!actualHours.value) {
      showToast({ message: '请输入实际工时', type: 'fail' })
      return
    }

    await completeTaskItem(task.value!.id, {
      shiji_gongshi: parseFloat(actualHours.value),
      beizhu: completeRemark.value || undefined
    })

    showToast({ message: '任务已完成', type: 'success' })
    showCompleteDialog.value = false
    await loadTask()
  } catch (error) {
    console.error('Complete task error:', error)
  }
}

const handlePause = async () => {
  try {
    await showConfirmDialog({
      title: '确认',
      message: '确定要暂停这个任务吗？'
    })

    await pauseTaskItem(task.value!.id, {})
    showToast({ message: '任务已暂停', type: 'success' })
    await loadTask()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Pause task error:', error)
    }
  }
}

const getStatusType = (status: TaskItemStatus) => {
  const typeMap: Record<TaskItemStatus, string> = {
    pending: 'warning',
    in_progress: 'primary',
    completed: 'success',
    skipped: 'default'
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status: TaskItemStatus) => {
  const textMap: Record<TaskItemStatus, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    skipped: '已跳过'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
.task-detail-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 20px;
}

.task-content {
  padding-top: 12px;
}

.task-description {
  padding: 12px 0;
  line-height: 1.6;
  color: #323233;
}

.action-buttons {
  margin: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>

