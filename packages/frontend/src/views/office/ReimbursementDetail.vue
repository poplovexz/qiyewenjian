<template>
  <div class="reimbursement-detail">
    <el-page-header @back="handleBack" content="报销申请详情" />

    <el-card class="detail-card" v-loading="loading">
      <!-- 基本信息 -->
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="申请编号">
          {{ detail.shenqing_bianhao }}
        </el-descriptions-item>
        <el-descriptions-item label="申请人">
          {{ detail.shenqing_ren_xingming }}
        </el-descriptions-item>
        <el-descriptions-item label="报销类型">
          <el-tag>{{ getTypeLabel(detail.baoxiao_leixing) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报销金额">
          <span class="amount">¥{{ detail.baoxiao_jine }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="报销事项时间">
          {{ formatDate(detail.baoxiao_shijian) }}
        </el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="getStatusType(detail.shenhe_zhuangtai)">
            {{ getStatusLabel(detail.shenhe_zhuangtai) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报销原因" :span="2">
          {{ detail.baoxiao_yuanyin }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2" v-if="detail.beizhu">
          {{ detail.beizhu }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(detail.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(detail.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 附件信息 -->
      <el-divider content-position="left">附件信息</el-divider>
      <div v-if="attachments.length > 0" class="attachments">
        <div v-for="(file, index) in attachments" :key="index" class="attachment-item">
          <el-link :href="file" target="_blank" type="primary">
            <el-icon><Document /></el-icon>
            附件{{ index + 1 }}
          </el-link>
        </div>
      </div>
      <el-empty v-else description="暂无附件" :image-size="80" />

      <!-- 审批流程 -->
      <el-divider content-position="left">审批流程</el-divider>
      <ApprovalWorkflow :workflow-id="detail.shenhe_liucheng_id" :records="auditRecords" />

      <!-- 操作按钮 -->
      <el-divider />
      <div class="action-buttons">
        <el-button @click="handleBack">返回</el-button>
        <el-button 
          v-if="canEdit" 
          type="primary" 
          @click="handleEdit"
        >
          编辑
        </el-button>
        <el-button 
          v-if="canSubmit" 
          type="success" 
          @click="handleSubmitApproval"
        >
          提交审批
        </el-button>
        <el-button 
          v-if="canApprove" 
          type="success" 
          @click="handleApprove"
        >
          审批通过
        </el-button>
        <el-button 
          v-if="canApprove" 
          type="danger" 
          @click="handleReject"
        >
          审批拒绝
        </el-button>
      </div>
    </el-card>

    <!-- 审批对话框 -->
    <ApprovalDialog
      v-model:visible="approvalDialogVisible"
      :default-action="approvalAction"
      @submit="handleApprovalSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import {
  getReimbursementDetail,
  submitReimbursementForApproval,
  approveReimbursement,
  rejectReimbursement,
  type ReimbursementApplication
} from '@/api/office'
import { useAuthStore } from '@/stores/modules/auth'
import ApprovalWorkflow from '@/components/office/ApprovalWorkflow.vue'
import ApprovalDialog from '@/components/office/ApprovalDialog.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const approvalDialogVisible = ref(false)
const approvalAction = ref<'tongguo' | 'jujue'>('tongguo')
const detail = ref<Partial<ReimbursementApplication>>({})
const auditRecords = ref<any[]>([])

const reimbursementId = computed(() => route.params.id as string)
const attachments = computed(() => {
  if (!detail.value.fujian_lujing) return []
  return detail.value.fujian_lujing.split(',').filter(Boolean)
})

const canEdit = computed(() => {
  return detail.value.shenhe_zhuangtai === 'daishehe'
})

const canSubmit = computed(() => {
  return detail.value.shenhe_zhuangtai === 'daishehe'
})

const canApprove = computed(() => {
  // TODO: 根据实际审批权限判断
  return detail.value.shenhe_zhuangtai === 'shenhezhong'
})

// 获取详情
const fetchDetail = async () => {
  loading.value = true
  try {
    const data = await getReimbursementDetail(reimbursementId.value)
    detail.value = data
    
    // TODO: 获取审批记录
    // if (data.shenhe_liucheng_id) {
    //   auditRecords.value = await getAuditRecords(data.shenhe_liucheng_id)
    // }
  } catch (error) {
    ElMessage.error('获取详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 编辑
const handleEdit = () => {
  router.push(`/office/reimbursement/edit/${reimbursementId.value}`)
}

// 提交审批
const handleSubmitApproval = async () => {
  try {
    await ElMessageBox.confirm('确定要提交审批吗？', '确认操作', {
      type: 'warning'
    })
    
    await submitReimbursementForApproval(reimbursementId.value)
    ElMessage.success('提交成功')
    fetchDetail()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  }
}

// 审批通过
const handleApprove = () => {
  approvalAction.value = 'tongguo'
  approvalDialogVisible.value = true
}

// 审批拒绝
const handleReject = () => {
  approvalAction.value = 'jujue'
  approvalDialogVisible.value = true
}

// 处理审批提交
const handleApprovalSubmit = async (data: { shenhe_jieguo: string; shenhe_yijian: string }) => {
  try {
    if (data.shenhe_jieguo === 'tongguo') {
      await approveReimbursement(reimbursementId.value, data.shenhe_yijian)
      ElMessage.success('审批通过')
    } else {
      await rejectReimbursement(reimbursementId.value, data.shenhe_yijian)
      ElMessage.success('已拒绝')
    }

    approvalDialogVisible.value = false
    fetchDetail()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 辅助函数
const getTypeLabel = (type: string) => {
  // 现在报销类型直接存储类别名称，无需映射
  return type || '-'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    daishehe: '待审核',
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daishehe: 'info',
    shenhezhong: 'warning',
    tongguo: 'success',
    jujue: 'danger'
  }
  return map[status] || 'info'
}



const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped lang="scss">
.reimbursement-detail {
  padding: 20px;

  .detail-card {
    margin-top: 20px;
  }

  .amount {
    color: #f56c6c;
    font-weight: bold;
    font-size: 16px;
  }

  .attachments {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;

    .attachment-item {
      padding: 8px 12px;
      background: #f5f7fa;
      border-radius: 4px;
    }
  }

  .audit-workflow {
    margin-top: 20px;
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
  }
}
</style>

