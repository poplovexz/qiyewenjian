<template>
  <div class="service-order-detail" v-loading="serviceOrderStore.loading">
    <div v-if="serviceOrder" class="detail-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-left">
          <el-button @click="goBack" circle>
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <h2>{{ serviceOrder.gongdan_biaoti }}</h2>
          <el-tag :type="getStatusType(serviceOrder.gongdan_zhuangtai)">
            {{ serviceOrderStore.statusMap[serviceOrder.gongdan_zhuangtai] }}
          </el-tag>
        </div>
        <div class="header-right">
          <el-button
            v-if="serviceOrder.gongdan_zhuangtai === 'created'"
            type="success"
            @click="showAssignDialog = true"
          >
            分配工单
          </el-button>
          <el-button
            v-if="serviceOrder.gongdan_zhuangtai === 'assigned'"
            type="warning"
            @click="startOrder"
          >
            开始执行
          </el-button>
          <el-button
            v-if="serviceOrder.gongdan_zhuangtai === 'in_progress'"
            type="primary"
            @click="showCompleteDialog = true"
          >
            完成工单
          </el-button>
          <el-button
            v-if="!['completed', 'cancelled'].includes(serviceOrder.gongdan_zhuangtai)"
            type="danger"
            @click="showCancelDialog = true"
          >
            取消工单
          </el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <!-- 左侧：工单信息 -->
        <el-col :span="16">
          <!-- 基本信息 -->
          <el-card title="基本信息" class="info-card">
            <template #header>
              <span>基本信息</span>
            </template>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="工单编号">
                {{ serviceOrder.gongdan_bianhao }}
              </el-descriptions-item>
              <el-descriptions-item label="服务类型">
                <el-tag>{{ serviceOrderStore.serviceTypeMap[serviceOrder.fuwu_leixing] }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityType(serviceOrder.youxian_ji)" size="small">
                  {{ serviceOrderStore.priorityMap[serviceOrder.youxian_ji] }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="进度">
                <el-progress
                  :percentage="serviceOrder.progress_percentage"
                  :color="getProgressColor(serviceOrder.progress_percentage)"
                />
              </el-descriptions-item>
              <el-descriptions-item label="计划开始时间">
                {{ formatDateTime(serviceOrder.jihua_kaishi_shijian) || '未设置' }}
              </el-descriptions-item>
              <el-descriptions-item label="计划结束时间">
                <span :class="{ 'overdue-text': serviceOrder.is_overdue }">
                  {{ formatDateTime(serviceOrder.jihua_jieshu_shijian) }}
                  <el-icon v-if="serviceOrder.is_overdue" color="#f56c6c"><Warning /></el-icon>
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="实际开始时间">
                {{ formatDateTime(serviceOrder.shiji_kaishi_shijian) || '未开始' }}
              </el-descriptions-item>
              <el-descriptions-item label="实际结束时间">
                {{ formatDateTime(serviceOrder.shiji_jieshu_shijian) || '未完成' }}
              </el-descriptions-item>
              <el-descriptions-item label="创建时间" :span="2">
                {{ formatDateTime(serviceOrder.created_at) }}
              </el-descriptions-item>
            </el-descriptions>

            <div v-if="serviceOrder.gongdan_miaoshu" class="description-section">
              <h4>工单描述</h4>
              <p>{{ serviceOrder.gongdan_miaoshu }}</p>
            </div>

            <div v-if="serviceOrder.wancheng_qingkuang" class="completion-section">
              <h4>完成情况</h4>
              <p>{{ serviceOrder.wancheng_qingkuang }}</p>
            </div>

            <div v-if="serviceOrder.kehu_pingjia" class="evaluation-section">
              <h4>客户评价</h4>
              <el-rate v-model="evaluationRating" disabled show-text text-color="#ff9900" />
              <p v-if="serviceOrder.kehu_pingjia_neirong">
                {{ serviceOrder.kehu_pingjia_neirong }}
              </p>
            </div>
          </el-card>

          <!-- 工单项目 -->
          <el-card title="工单项目" class="items-card">
            <template #header>
              <span>工单项目</span>
            </template>

            <el-table :data="serviceOrder.xiangmu_list" stripe>
              <el-table-column prop="paixu" label="序号" width="80" />
              <el-table-column prop="xiangmu_mingcheng" label="项目名称" min-width="200" />
              <el-table-column prop="xiangmu_miaoshu" label="项目描述" min-width="200" />
              <el-table-column prop="xiangmu_zhuangtai" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getItemStatusType(row.xiangmu_zhuangtai)" size="small">
                    {{ getItemStatusText(row.xiangmu_zhuangtai) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="zhixing_ren" label="执行人" width="120">
                <template #default="{ row }">
                  {{ row.zhixing_ren?.xingming || '未分配' }}
                </template>
              </el-table-column>
              <el-table-column prop="jihua_gongshi" label="计划工时" width="100">
                <template #default="{ row }"> {{ row.jihua_gongshi || '-' }}h </template>
              </el-table-column>
              <el-table-column prop="shiji_gongshi" label="实际工时" width="100">
                <template #default="{ row }"> {{ row.shiji_gongshi || '-' }}h </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" size="small" link @click="handleAssignTaskItem(row)">
                    {{ row.zhixing_ren ? '重新分配' : '分配' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 右侧：操作日志和评论 -->
        <el-col :span="8">
          <!-- 操作日志 -->
          <el-card title="操作日志" class="log-card">
            <template #header>
              <span>操作日志</span>
            </template>

            <el-timeline>
              <el-timeline-item
                v-for="log in serviceOrder.rizhi_list"
                :key="log.id"
                :timestamp="formatDateTime(log.created_at)"
                placement="top"
              >
                <div class="log-content">
                  <div class="log-type">{{ getLogTypeText(log.caozuo_leixing) }}</div>
                  <div class="log-description">{{ log.caozuo_neirong }}</div>
                  <div v-if="log.fujian_lujing" class="log-attachment">
                    <el-link :href="log.fujian_lujing" target="_blank" rel="noopener noreferrer">
                      <el-icon><Paperclip /></el-icon>
                      查看附件
                    </el-link>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>

          <!-- 添加评论 -->
          <el-card title="添加评论" class="comment-card">
            <template #header>
              <span>添加评论</span>
            </template>

            <el-form @submit.prevent="addComment">
              <el-form-item>
                <el-input
                  v-model="commentForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入评论内容..."
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="addComment" :loading="commentLoading">
                  添加评论
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分配工单对话框 -->
    <AssignOrderDialog
      v-model:visible="showAssignDialog"
      :order="serviceOrder"
      @success="handleAssignSuccess"
    />

    <!-- 完成工单对话框 -->
    <CompleteOrderDialog
      v-model:visible="showCompleteDialog"
      :order="serviceOrder"
      @success="handleCompleteSuccess"
    />

    <!-- 取消工单对话框 -->
    <CancelOrderDialog
      v-model:visible="showCancelDialog"
      :order="serviceOrder"
      @success="handleCancelSuccess"
    />

    <!-- 分配任务项对话框 -->
    <AssignTaskItemDialog
      v-model="showAssignTaskItemDialog"
      :task-item="currentTaskItem"
      :gongdan-id="serviceOrder?.id || ''"
      @success="handleAssignTaskItemSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Warning, Paperclip } from '@element-plus/icons-vue'
import {
  useServiceOrderStore,
  type ServiceOrderItem,
} from '@/stores/modules/serviceOrderManagement'
import AssignOrderDialog from './components/AssignOrderDialog.vue'
import CompleteOrderDialog from './components/CompleteOrderDialog.vue'
import CancelOrderDialog from './components/CancelOrderDialog.vue'
import AssignTaskItemDialog from './components/AssignTaskItemDialog.vue'
import { formatDateTime } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const serviceOrderStore = useServiceOrderStore()

// 响应式数据
const showAssignDialog = ref(false)
const showCompleteDialog = ref(false)
const showCancelDialog = ref(false)
const showAssignTaskItemDialog = ref(false)
const currentTaskItem = ref<ServiceOrderItem | null>(null)
const commentLoading = ref(false)

const commentForm = reactive({
  content: '',
})

// 计算属性
const serviceOrder = computed(() => serviceOrderStore.currentServiceOrder)

const evaluationRating = computed(() => {
  const ratingMap: Record<string, number> = {
    excellent: 5,
    good: 4,
    average: 3,
    poor: 2,
  }
  return ratingMap[serviceOrder.value?.kehu_pingjia || ''] || 0
})

// 方法
const loadData = async () => {
  const orderId = route.params.id as string
  try {
    await serviceOrderStore.fetchServiceOrderDetail(orderId)
  } catch (error) {
    ElMessage.error('加载工单详情失败')
  }
}

const goBack = () => {
  router.back()
}

const startOrder = async () => {
  try {
    await ElMessageBox.confirm('确认开始执行此工单？', '确认操作', {
      type: 'warning',
    })

    await serviceOrderStore.startServiceOrder(serviceOrder.value!.id)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
    }
  }
}

const addComment = async () => {
  if (!commentForm.content.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  commentLoading.value = true
  try {
    await serviceOrderStore.addServiceOrderComment(serviceOrder.value!.id, commentForm.content)
    commentForm.content = ''
    loadData()
  } catch (error) {
  } finally {
    commentLoading.value = false
  }
}

const handleAssignSuccess = () => {
  showAssignDialog.value = false
  loadData()
}

const handleCompleteSuccess = () => {
  showCompleteDialog.value = false
  loadData()
}

const handleCancelSuccess = () => {
  showCancelDialog.value = false
  loadData()
}

// 辅助方法
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    created: 'info',
    assigned: 'warning',
    in_progress: 'primary',
    pending_review: 'warning',
    completed: 'success',
    cancelled: 'danger',
  }
  return typeMap[status] || 'info'
}

const getPriorityType = (priority: string) => {
  const typeMap: Record<string, string> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    urgent: 'danger',
  }
  return typeMap[priority] || 'info'
}

const getProgressColor = (percentage: number) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const getItemStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    skipped: 'info',
  }
  return typeMap[status] || 'info'
}

const getItemStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    skipped: '已跳过',
  }
  return textMap[status] || status
}

const getLogTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    created: '创建',
    assigned: '分配',
    started: '开始',
    paused: '暂停',
    completed: '完成',
    cancelled: '取消',
    commented: '评论',
    status_changed: '状态变更',
    task_assign: '任务分配',
  }
  return textMap[type] || type
}

// 分配任务项
const handleAssignTaskItem = (taskItem: ServiceOrderItem) => {
  currentTaskItem.value = taskItem
  showAssignTaskItemDialog.value = true
}

// 分配任务项成功
const handleAssignTaskItemSuccess = async () => {
  await loadData()
  ElMessage.success('任务项分配成功')
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.service-order-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 10px;
}

.info-card,
.items-card,
.log-card,
.comment-card {
  margin-bottom: 20px;
}

.description-section,
.completion-section,
.evaluation-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.description-section h4,
.completion-section h4,
.evaluation-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.log-content {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.log-type {
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.log-description {
  color: #606266;
  margin-bottom: 5px;
}

.log-attachment {
  margin-top: 5px;
}

.overdue-text {
  color: #f56c6c;
  font-weight: bold;
}
</style>
