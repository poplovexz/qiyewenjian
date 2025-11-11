<template>
  <div class="payment-audit-container">
    <el-card class="page-header">
      <div class="header-content">
        <h2>支付订单审核</h2>
        <p>管理支付订单的审核流程，包括触发审核、审批和查看状态</p>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" class="audit-tabs">
      <!-- 待审批订单 -->
      <el-tab-pane label="待审批订单" name="pending">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的待审批支付订单</span>
              <el-button type="primary" @click="refreshPendingList">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <el-table 
            :data="pendingList" 
            v-loading="pendingLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="order_name" label="订单名称" min-width="200" />
            <el-table-column prop="payment_amount" label="支付金额" width="120">
              <template #default="{ row }">
                <span class="amount">¥{{ row.payment_amount.toLocaleString() }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="payment_type" label="支付类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getPaymentTypeTag(row.payment_type)">
                  {{ getPaymentTypeName(row.payment_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="audit_status" label="审核状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getAuditStatusTag(row.audit_status)">
                  {{ getAuditStatusName(row.audit_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleApprove(row)"
                >
                  审批
                </el-button>
                <el-button 
                  type="danger" 
                  size="small"
                  @click="handleReject(row)"
                >
                  拒绝
                </el-button>
                <el-button 
                  type="info" 
                  size="small"
                  @click="viewDetails(row)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="pendingTotal > 0"
            v-model:current-page="pendingPage"
            v-model:page-size="pendingSize"
            :total="pendingTotal"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePendingSizeChange"
            @current-change="handlePendingPageChange"
            style="margin-top: 20px; text-align: right"
          />
        </el-card>
      </el-tab-pane>

      <!-- 支付订单查询 -->
      <el-tab-pane label="订单查询" name="search">
        <el-card>
          <template #header>
            <span>支付订单审核状态查询</span>
          </template>

          <el-form :model="searchForm" inline class="search-form">
            <el-form-item label="订单ID">
              <el-input 
                v-model="searchForm.payment_order_id" 
                placeholder="请输入支付订单ID"
                style="width: 300px"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchPaymentStatus">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetSearch">重置</el-button>
            </el-form-item>
          </el-form>

          <div v-if="searchResult" class="search-result">
            <el-descriptions title="支付订单审核状态" :column="2" border>
              <el-descriptions-item label="订单ID">
                {{ searchResult.payment_order_id }}
              </el-descriptions-item>
              <el-descriptions-item label="审核状态">
                <el-tag :type="getAuditStatusTag(searchResult.audit_status)">
                  {{ getAuditStatusName(searchResult.audit_status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="支付状态">
                <el-tag :type="getPaymentStatusTag(searchResult.payment_status)">
                  {{ getPaymentStatusName(searchResult.payment_status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前审批人">
                {{ searchResult.current_approver || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ formatDate(searchResult.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="更新时间">
                {{ formatDate(searchResult.updated_at) }}
              </el-descriptions-item>
            </el-descriptions>

            <div style="margin-top: 20px">
              <el-button 
                type="primary" 
                @click="viewAuditHistory(searchResult.payment_order_id)"
              >
                查看审核历史
              </el-button>
              <el-button 
                v-if="searchResult.audit_status === 'not_required'"
                type="warning" 
                @click="triggerAudit(searchResult.payment_order_id)"
              >
                触发审核
              </el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 审批对话框 -->
    <el-dialog 
      v-model="approvalDialogVisible" 
      title="支付订单审批" 
      width="600px"
    >
      <el-form :model="approvalForm" label-width="100px">
        <el-form-item label="订单名称">
          <span>{{ currentRecord?.order_name }}</span>
        </el-form-item>
        <el-form-item label="支付金额">
          <span class="amount">¥{{ currentRecord?.payment_amount?.toLocaleString() }}</span>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input 
            v-model="approvalForm.approval_comment"
            type="textarea"
            :rows="4"
            placeholder="请输入审批意见"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="approvalDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmApproval" :loading="approvalLoading">
          通过
        </el-button>
      </template>
    </el-dialog>

    <!-- 拒绝对话框 -->
    <el-dialog 
      v-model="rejectionDialogVisible" 
      title="拒绝支付订单" 
      width="600px"
    >
      <el-form :model="rejectionForm" label-width="100px">
        <el-form-item label="订单名称">
          <span>{{ currentRecord?.order_name }}</span>
        </el-form-item>
        <el-form-item label="支付金额">
          <span class="amount">¥{{ currentRecord?.payment_amount?.toLocaleString() }}</span>
        </el-form-item>
        <el-form-item label="拒绝原因" required>
          <el-input 
            v-model="rejectionForm.rejection_reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="rejectionDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmRejection" :loading="rejectionLoading">
          确认拒绝
        </el-button>
      </template>
    </el-dialog>

    <!-- 审核历史对话框 -->
    <el-dialog 
      v-model="historyDialogVisible" 
      title="审核历史" 
      width="800px"
    >
      <div v-if="auditHistory.length > 0">
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in auditHistory"
            :key="index"
            :timestamp="formatDate(record.created_at)"
            placement="top"
          >
            <el-card>
              <div class="history-item">
                <div class="history-header">
                  <span class="history-status">
                    <el-tag :type="getAuditStatusTag(record.audit_status)">
                      {{ getAuditStatusName(record.audit_status) }}
                    </el-tag>
                  </span>
                  <span class="history-applicant">申请人: {{ record.applicant_id }}</span>
                </div>
                
                <div v-if="record.steps.length > 0" class="history-steps">
                  <h4>审核步骤:</h4>
                  <el-table :data="record.steps" size="small">
                    <el-table-column prop="step_order" label="步骤" width="60" />
                    <el-table-column prop="step_name" label="步骤名称" />
                    <el-table-column prop="approver_id" label="审批人" />
                    <el-table-column prop="approval_status" label="状态" width="100">
                      <template #default="{ row }">
                        <el-tag size="small" :type="getApprovalStatusTag(row.approval_status)">
                          {{ getApprovalStatusName(row.approval_status) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="approval_time" label="审批时间" width="180">
                      <template #default="{ row }">
                        {{ row.approval_time ? formatDate(row.approval_time) : '-' }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      <el-empty v-else description="暂无审核历史" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'

// 响应式数据
const activeTab = ref('pending')
const pendingList = ref([])
const pendingLoading = ref(false)
const pendingPage = ref(1)
const pendingSize = ref(20)
const pendingTotal = ref(0)

const searchForm = reactive({
  payment_order_id: ''
})
const searchResult = ref(null)

const approvalDialogVisible = ref(false)
const rejectionDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const currentRecord = ref(null)
const approvalLoading = ref(false)
const rejectionLoading = ref(false)

const approvalForm = reactive({
  approval_comment: ''
})

const rejectionForm = reactive({
  rejection_reason: ''
})

const auditHistory = ref([])

// 方法
const refreshPendingList = async () => {
  pendingLoading.value = true
  try {
    const response = await fetch(`/payment-audit/pending/my?page=${pendingPage.value}&size=${pendingSize.value}`)
    const data = await response.json()
    
    if (response.ok) {
      pendingList.value = data.items
      pendingTotal.value = data.total
    } else {
      ElMessage.error(data.detail || '获取待审批列表失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    pendingLoading.value = false
  }
}

const handlePendingSizeChange = (size: number) => {
  pendingSize.value = size
  pendingPage.value = 1
  refreshPendingList()
}

const handlePendingPageChange = (page: number) => {
  pendingPage.value = page
  refreshPendingList()
}

const searchPaymentStatus = async () => {
  if (!searchForm.payment_order_id.trim()) {
    ElMessage.warning('请输入支付订单ID')
    return
  }

  try {
    const response = await fetch(`/payment-audit/status/${searchForm.payment_order_id}`)
    const data = await response.json()
    
    if (response.ok) {
      searchResult.value = data
    } else {
      ElMessage.error(data.detail || '查询失败')
      searchResult.value = null
    }
  } catch (error) {
    ElMessage.error('网络错误')
    searchResult.value = null
  }
}

const resetSearch = () => {
  searchForm.payment_order_id = ''
  searchResult.value = null
}

const handleApprove = (record: any) => {
  currentRecord.value = record
  approvalForm.approval_comment = ''
  approvalDialogVisible.value = true
}

const handleReject = (record: any) => {
  currentRecord.value = record
  rejectionForm.rejection_reason = ''
  rejectionDialogVisible.value = true
}

const confirmApproval = async () => {
  approvalLoading.value = true
  try {
    const response = await fetch('/payment-audit/approve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        audit_record_id: currentRecord.value.audit_record_id,
        approval_comment: approvalForm.approval_comment
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success('审批成功')
      approvalDialogVisible.value = false
      refreshPendingList()
    } else {
      ElMessage.error(data.detail || '审批失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    approvalLoading.value = false
  }
}

const confirmRejection = async () => {
  if (!rejectionForm.rejection_reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }

  rejectionLoading.value = true
  try {
    const response = await fetch('/payment-audit/reject', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        audit_record_id: currentRecord.value.audit_record_id,
        rejection_reason: rejectionForm.rejection_reason
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success('拒绝成功')
      rejectionDialogVisible.value = false
      refreshPendingList()
    } else {
      ElMessage.error(data.detail || '拒绝失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    rejectionLoading.value = false
  }
}

const viewDetails = (record: any) => {
  // 查看详情逻辑
  ElMessage.info('查看详情功能开发中')
}

const viewAuditHistory = async (paymentOrderId: string) => {
  try {
    const response = await fetch(`/payment-audit/history/${paymentOrderId}`)
    const data = await response.json()
    
    if (response.ok) {
      auditHistory.value = data.audit_history
      historyDialogVisible.value = true
    } else {
      ElMessage.error(data.detail || '获取审核历史失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  }
}

const triggerAudit = async (paymentOrderId: string) => {
  try {
    await ElMessageBox.confirm('确认要触发该支付订单的审核流程吗？', '确认操作', {
      type: 'warning'
    })

    const response = await fetch('/payment-audit/trigger', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        payment_order_id: paymentOrderId
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success('审核流程已触发')
      searchPaymentStatus()
    } else {
      ElMessage.error(data.detail || '触发审核失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('网络错误')
    }
  }
}

// 辅助方法
const getPaymentTypeTag = (type: string) => {
  const typeMap = {
    'weixin': 'success',
    'zhifubao': 'primary',
    'yinhangzhuanzhang': 'warning',
    'xianjin': 'danger',
    'qita': 'info'
  }
  return typeMap[type] || 'info'
}

const getPaymentTypeName = (type: string) => {
  const nameMap = {
    'weixin': '微信支付',
    'zhifubao': '支付宝',
    'yinhangzhuanzhang': '银行转账',
    'xianjin': '现金',
    'qita': '其他'
  }
  return nameMap[type] || type
}

const getAuditStatusTag = (status: string) => {
  const statusMap = {
    'pending': 'warning',
    'in_progress': 'primary',
    'approved': 'success',
    'rejected': 'danger',
    'not_required': 'info'
  }
  return statusMap[status] || 'info'
}

const getAuditStatusName = (status: string) => {
  const nameMap = {
    'pending': '待审核',
    'in_progress': '审核中',
    'approved': '已通过',
    'rejected': '已拒绝',
    'not_required': '无需审核'
  }
  return nameMap[status] || status
}

const getPaymentStatusTag = (status: string) => {
  const statusMap = {
    'pending': 'warning',
    'paying': 'primary',
    'paid': 'success',
    'failed': 'danger',
    'cancelled': 'info',
    'approved': 'success',
    'audit_rejected': 'danger'
  }
  return statusMap[status] || 'info'
}

const getPaymentStatusName = (status: string) => {
  const nameMap = {
    'pending': '待支付',
    'paying': '支付中',
    'paid': '已支付',
    'failed': '支付失败',
    'cancelled': '已取消',
    'approved': '审核通过',
    'audit_rejected': '审核拒绝'
  }
  return nameMap[status] || status
}

const getApprovalStatusTag = (status: string) => {
  const statusMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return statusMap[status] || 'info'
}

const getApprovalStatusName = (status: string) => {
  const nameMap = {
    'pending': '待审批',
    'approved': '已通过',
    'rejected': '已拒绝'
  }
  return nameMap[status] || status
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  refreshPendingList()
})
</script>

<style scoped>
.payment-audit-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.header-content p {
  margin: 0;
  color: #606266;
}

.audit-tabs {
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount {
  font-weight: bold;
  color: #E6A23C;
}

.search-form {
  margin-bottom: 20px;
}

.search-result {
  margin-top: 20px;
}

.history-item {
  padding: 10px 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.history-status {
  font-weight: bold;
}

.history-applicant {
  color: #606266;
  font-size: 14px;
}

.history-steps h4 {
  margin: 10px 0;
  color: #303133;
}
</style>
