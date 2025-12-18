<template>
  <el-dialog
    v-model="dialogVisible"
    title="审核流程详情"
    width="800px"
    :before-close="handleClose"
  >
    <div v-loading="loading" class="audit-detail-dialog">
      <div v-if="workflowDetail" class="workflow-detail">
        <!-- 基本信息 -->
        <div class="basic-info-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="流程编号">
              {{ workflowDetail.workflow_number }}
            </el-descriptions-item>
            <el-descriptions-item label="审核类型">
              <el-tag :type="getAuditTypeTagType(workflowDetail.audit_type)">
                {{ getAuditTypeText(workflowDetail.audit_type) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审核状态">
              <el-tag :type="getStatusTagType(workflowDetail.status)">
                {{ getStatusText(workflowDetail.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="申请人">
              {{ workflowDetail.submitter }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(workflowDetail.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="完成时间">
              {{ workflowDetail.wancheng_shijian ? formatDateTime(workflowDetail.wancheng_shijian) : '未完成' }}
            </el-descriptions-item>
            <el-descriptions-item label="申请原因" :span="2">
              {{ workflowDetail.shenqing_yuanyin || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 银行汇款审核特殊信息 -->
        <div v-if="workflowDetail.audit_type === 'yinhang_huikuan' && workflowDetail.trigger_data" class="bank-transfer-section">
          <h4>汇款信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="单据编号">
              {{ workflowDetail.trigger_data.danju_bianhao || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="汇款金额">
              <span style="color: #f56c6c; font-weight: bold;">
                ¥{{ workflowDetail.trigger_data.huikuan_jine?.toFixed(2) || '0.00' }}
              </span>
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="workflowDetail.trigger_data.voucher_url" class="voucher-preview" style="margin-top: 15px;">
            <h5>汇款凭证</h5>
            <el-image
              :src="getImageUrl(workflowDetail.trigger_data.voucher_url)"
              :preview-src-list="[getImageUrl(workflowDetail.trigger_data.voucher_url)]"
              fit="contain"
              style="width: 100%; max-width: 500px; border: 1px solid #dcdfe6; border-radius: 4px;"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                  <span>图片加载失败</span>
                </div>
              </template>
            </el-image>
          </div>
        </div>

        <!-- 审核步骤 -->
        <div class="steps-section">
          <h4>审核步骤</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(record, index) in auditRecords"
              :key="record.id"
              :timestamp="formatDateTime(record.created_at)"
              :type="getTimelineType(record.jilu_zhuangtai)"
              :icon="getTimelineIcon(record.jilu_zhuangtai)"
            >
              <el-card class="step-card">
                <div class="step-header">
                  <div class="step-title">
                    <span class="step-name">{{ record.buzhou_mingcheng }}</span>
                    <el-tag
                      :type="getRecordStatusTagType(record.jilu_zhuangtai)"
                      size="small"
                    >
                      {{ getRecordStatusText(record.jilu_zhuangtai) }}
                    </el-tag>
                  </div>
                  <div class="step-info">
                    <span class="auditor">审核人：{{ record.shenhe_ren_mingcheng || '待分配' }}</span>
                  </div>
                </div>

                <div v-if="record.shenhe_yijian" class="step-content">
                  <div class="audit-opinion">
                    <strong>审核意见：</strong>
                    <p>{{ record.shenhe_yijian }}</p>
                  </div>
                </div>

                <div v-if="record.fujian_lujing" class="step-attachments">
                  <strong>附件：</strong>
                  <el-link
                    :href="getFileUrl(record.fujian_lujing)"
                    target="_blank"
                    rel="noopener noreferrer"
                    type="primary"
                  >
                    {{ record.fujian_miaoshu || '查看附件' }}
                  </el-link>
                </div>

                <div class="step-footer">
                  <div class="step-time">
                    <span v-if="record.shenhe_shijian">
                      处理时间：{{ formatDateTime(record.shenhe_shijian) }}
                    </span>
                    <span v-else-if="record.qiwang_shijian">
                      期望处理时间：{{ formatDateTime(record.qiwang_shijian) }}
                    </span>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 关联信息 -->
        <div v-if="workflowDetail.guanlian_xinxi" class="related-info-section">
          <h4>关联信息</h4>
          <el-card>
            <pre>{{ JSON.stringify(workflowDetail.guanlian_xinxi, null, 2) }}</pre>
          </el-card>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          v-if="canCancel"
          type="danger"
          @click="handleCancel"
        >
          取消流程
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock,
  Check,
  Close,
  Warning,
  Picture
} from '@element-plus/icons-vue'
import { useAuditManagementStore } from '@/stores/modules/auditManagement'

// Props
interface Props {
  visible: boolean
  workflowId: string
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  workflowId: ''
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

// 使用store
const auditStore = useAuditManagementStore()

// 响应式数据
const loading = ref(false)
const workflowDetail = ref<any>(null)
const auditRecords = ref<any[]>([])

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const canCancel = computed(() => {
  return workflowDetail.value?.shenhe_zhuangtai === 'shenhezhong'
})

// 方法
const handleClose = () => {
  emit('update:visible', false)
}

const fetchWorkflowDetail = async () => {
  if (!props.workflowId) return

  try {
    loading.value = true

    // 获取流程详情（包含审核记录）
    const detail = await auditStore.fetchAuditWorkflowById(props.workflowId)
    workflowDetail.value = detail

    // 使用流程详情中的审核记录
    auditRecords.value = detail.shenhe_jilu || []

  } catch (error) {
    console.error('获取审核流程详情失败:', error)
    ElMessage.error('获取审核流程详情失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = async () => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      '请输入取消原因',
      '取消审核流程',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputValidator: (value) => {
          if (!value || value.trim().length === 0) {
            return '请输入取消原因'
          }
          return true
        }
      }
    )

    await auditStore.cancelAuditWorkflow(props.workflowId, reason)
    
    // 重新获取详情
    await fetchWorkflowDetail()
    
    emit('success')
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('取消审核流程失败:', error)
      ElMessage.error('取消审核流程失败')
    }
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

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    shenhezhong: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    chexiao: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝',
    chexiao: '已取消'
  }
  return texts[status] || status
}

const getRecordStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    daichuli: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    zhuanfa: 'info'
  }
  return types[status] || 'info'
}

const getRecordStatusText = (status: string) => {
  const texts: Record<string, string> = {
    daichuli: '待处理',
    tongguo: '已通过',
    jujue: '已拒绝',
    zhuanfa: '已转发'
  }
  return texts[status] || status
}

const getTimelineType = (status: string) => {
  const types: Record<string, string> = {
    daichuli: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    zhuanfa: 'info'
  }
  return types[status] || 'info'
}

const getTimelineIcon = (status: string) => {
  const icons: Record<string, any> = {
    daichuli: Clock,
    tongguo: Check,
    jujue: Close,
    zhuanfa: Warning
  }
  return icons[status] || Clock
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

const getFileUrl = (filePath: string) => {
  return `${import.meta.env.VITE_API_BASE_URL}/files/${filePath}`
}

const getImageUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  return `http://localhost:8000${path}`
}

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  if (newVal && props.workflowId) {
    fetchWorkflowDetail()
  }
})
</script>

<style scoped>
.audit-detail-dialog {
  max-height: 600px;
  overflow-y: auto;
}

.basic-info-section,
.steps-section,
.related-info-section,
.bank-transfer-section {
  margin-bottom: 24px;
}

.basic-info-section h4,
.steps-section h4,
.related-info-section h4,
.bank-transfer-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.step-card {
  margin-bottom: 8px;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-name {
  font-weight: 600;
  color: #303133;
}

.step-info {
  color: #909399;
  font-size: 14px;
}

.step-content {
  margin-bottom: 12px;
}

.audit-opinion p {
  margin: 8px 0 0 0;
  color: #606266;
  line-height: 1.5;
}

.step-attachments {
  margin-bottom: 12px;
}

.step-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 12px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 12px;
}

.voucher-preview h5 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
  background-color: #f5f7fa;
}

.image-error .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}
</style>
