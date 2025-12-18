<template>
  <div class="audit-task-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>我的审核任务</h2>
      <p>处理待审核的合同和报价</p>
    </div>

    <!-- 统计卡片 -->
    <div class="statistics-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ pendingAuditsCount }}</div>
              <div class="stat-label">待处理任务</div>
            </div>
            <el-icon class="stat-icon pending"><Clock /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ myStatistics.processed_count || 0 }}</div>
              <div class="stat-label">已处理任务</div>
            </div>
            <el-icon class="stat-icon processed"><Check /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ myStatistics.processing_rate || 0 }}%</div>
              <div class="stat-label">处理率</div>
            </div>
            <el-icon class="stat-icon rate"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ overdueCount }}</div>
              <div class="stat-label">超期任务</div>
            </div>
            <el-icon class="stat-icon overdue"><Warning /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>审核任务</span>
          <div class="header-actions">
            <el-button @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待审核" name="pending">
          <div v-loading="auditStore.loading">
            <div v-if="pendingAudits.length === 0" class="empty-state">
              <el-empty description="暂无待审核任务">
                <el-button type="primary" @click="handleRefresh">刷新任务</el-button>
              </el-empty>
            </div>

            <div v-else class="task-list">
          <div
            v-for="task in pendingAudits"
            :key="task.step_id"
            class="task-item"
            :class="{ 'overdue': isOverdue(task.expected_time) }"
          >
            <div class="task-header">
              <div class="task-title">
                <el-tag :type="getAuditTypeTagType(task.audit_type)">
                  {{ getAuditTypeText(task.audit_type) }}
                </el-tag>
                <span class="workflow-number">{{ task.workflow_number }}</span>
                <span v-if="isOverdue(task.expected_time)" class="overdue-badge">
                  <el-icon><Warning /></el-icon>
                  超期
                </span>
              </div>
              <div class="task-actions">
                <el-button type="primary" size="small" @click="handleAudit(task)">
                  审核
                </el-button>
                <el-button size="small" @click="handleViewDetail(task)">
                  查看详情
                </el-button>
              </div>
            </div>

            <div class="task-content">
              <div class="task-info">
                <div class="info-item">
                  <span class="label">审核步骤：</span>
                  <span class="value">{{ task.step_name }}</span>
                </div>
                <div class="info-item">
                  <span class="label">关联对象：</span>
                  <span class="value">{{ task.related_info?.name || '未知' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">申请原因：</span>
                  <span class="value">{{ task.applicant_reason || '无' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">期望处理时间：</span>
                  <span class="value">{{ formatDateTime(task.expected_time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="已处理" name="processed">
          <div v-loading="loadingProcessed">
            <div v-if="processedAudits.length === 0" class="empty-state">
              <el-empty description="暂无已处理任务" />
            </div>

            <div v-else class="task-list">
              <div
                v-for="task in processedAudits"
                :key="task.step_id"
                class="task-item processed"
              >
                <div class="task-header">
                  <div class="task-title">
                    <el-tag :type="getAuditTypeTagType(task.audit_type)">
                      {{ getAuditTypeText(task.audit_type) }}
                    </el-tag>
                    <span class="workflow-number">{{ task.workflow_number }}</span>
                    <el-tag
                      :type="task.shenhe_jieguo === 'tongguo' ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ task.shenhe_jieguo === 'tongguo' ? '已通过' : '已拒绝' }}
                    </el-tag>
                  </div>
                  <div class="task-actions">
                    <el-button size="small" @click="handleViewDetail(task)">
                      查看详情
                    </el-button>
                  </div>
                </div>

                <div class="task-content">
                  <div class="task-info">
                    <div class="info-item">
                      <span class="label">审核步骤：</span>
                      <span class="value">{{ task.step_name }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">关联对象：</span>
                      <span class="value">{{ task.related_info?.name || '未知' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">申请原因：</span>
                      <span class="value">{{ task.applicant_reason || '无' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">处理时间：</span>
                      <span class="value">{{ formatDate(task.shenhe_shijian) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">审核意见：</span>
                      <span class="value">{{ task.shenhe_yijian || '无' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 审核对话框 -->
    <AuditActionDialog
      v-model:visible="auditDialogVisible"
      :task="currentTask"
      @success="handleAuditSuccess"
    />

    <!-- 详情对话框 -->
    <AuditDetailDialog
      v-model:visible="detailDialogVisible"
      :workflow-id="currentWorkflowId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Clock,
  Check,
  TrendCharts,
  Warning,
  Refresh
} from '@element-plus/icons-vue'
import { useAuditManagementStore } from '@/stores/modules/auditManagement'
import { storeToRefs } from 'pinia'
import AuditActionDialog from '@/components/audit/AuditActionDialog.vue'
import AuditDetailDialog from '@/components/audit/AuditDetailDialog.vue'

// 使用store
const auditStore = useAuditManagementStore()
const { pendingAudits, pendingAuditsCount } = storeToRefs(auditStore)

// 响应式数据
const activeTab = ref('pending')
const auditDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentTask = ref<any>(null)
const currentWorkflowId = ref('')
const myStatistics = ref<any>({})
const overdueCount = ref(0)
const processedAudits = ref<any[]>([])
const loadingProcessed = ref(false)

// 计算属性
const isOverdue = (expectedTime: string) => {
  return new Date(expectedTime) < new Date()
}

// 方法
const handleTabChange = async (tabName: string) => {
  if (tabName === 'processed') {
    await fetchProcessedAudits()
  }
}

const fetchProcessedAudits = async () => {
  try {
    loadingProcessed.value = true
    // 使用auditRecordApi获取已处理的审核任务
    const { auditRecordApi } = await import('@/api/modules/audit')
    const response = await auditRecordApi.getMyProcessed()

    

    // 处理响应数据
    if (response && response.data) {
      processedAudits.value = response.data.items || response.data || []
    } else if (response) {
      processedAudits.value = response.items || response || []
    } else {
      processedAudits.value = []
    }

    
  } catch (error) {
    console.error('获取已处理任务失败:', error)
    ElMessage.error('获取已处理任务失败')
  } finally {
    loadingProcessed.value = false
  }
}

const handleRefresh = async () => {
  if (activeTab.value === 'pending') {
    await Promise.all([
      auditStore.fetchMyPendingAudits(),
      fetchMyStatistics(),
      fetchOverdueCount()
    ])
  } else {
    await fetchProcessedAudits()
  }
  ElMessage.success('刷新成功')
}

const handleAudit = (task: any) => {
  currentTask.value = task
  auditDialogVisible.value = true
}

const handleViewDetail = (task: any) => {
  currentWorkflowId.value = task.workflow_id
  detailDialogVisible.value = true
}

const handleAuditSuccess = () => {
  auditDialogVisible.value = false
  handleRefresh()
}

const fetchMyStatistics = async () => {
  try {
    myStatistics.value = await auditStore.fetchMyAuditStatistics()
  } catch (error) {
    console.error('获取我的审核统计失败:', error)
  }
}

const fetchOverdueCount = async () => {
  try {
    // 这里应该调用获取超期任务数量的API
    overdueCount.value = pendingAudits.value.filter(task => isOverdue(task.expected_time)).length
  } catch (error) {
    console.error('获取超期任务数量失败:', error)
  }
}

const getAuditTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    yinhang_huikuan: 'danger',
    hetong: 'primary',
    hetong_jine_xiuzheng: 'warning',
    baojia: 'success',
    baojia_shenhe: 'success'
  }
  return types[type] || 'info'
}

const getAuditTypeText = (type: string) => {
  const texts: Record<string, string> = {
    yinhang_huikuan: '银行汇款审核',
    hetong: '合同审核',
    hetong_jine_xiuzheng: '合同金额修正',
    baojia: '报价审核',
    baojia_shenhe: '报价审核'
  }
  return texts[type] || type
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(async () => {
  await handleRefresh()
})
</script>

<style scoped>
.audit-task-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  opacity: 0.3;
}

.stat-icon.pending {
  color: #E6A23C;
}

.stat-icon.processed {
  color: #67C23A;
}

.stat-icon.rate {
  color: #409EFF;
}

.stat-icon.overdue {
  color: #F56C6C;
}

.task-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.task-list {
  space-y: 16px;
}

.task-item {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.task-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.task-item.overdue {
  border-color: #F56C6C;
  background-color: #FEF0F0;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-number {
  font-weight: bold;
  color: #303133;
}

.overdue-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #F56C6C;
  font-size: 12px;
}

.task-content {
  margin-top: 12px;
}

.task-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  color: #909399;
  margin-right: 8px;
  min-width: 100px;
}

.info-item .value {
  color: #303133;
  flex: 1;
}
</style>
