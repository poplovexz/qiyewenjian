<template>
  <div class="leave-detail-container">
    <van-nav-bar
      title="请假申请详情"
      left-arrow
      fixed
      placeholder
      @click-left="onBack"
    >
      <template #right>
        <van-icon v-if="canEdit" name="edit" @click="goToEdit" />
      </template>
    </van-nav-bar>

    <van-loading v-if="loading" class="loading" />

    <div v-else>
      <!-- 基本信息 -->
      <van-cell-group inset title="基本信息">
        <van-cell title="申请编号" :value="detail.shenqing_bianhao" />
        <van-cell title="申请人" :value="detail.shenqing_ren_xingming" />
        <van-cell title="请假类型" :value="getLeaveTypeText(detail.qingjia_leixing)" />
        <van-cell title="开始时间" :value="formatDateTime(detail.kaishi_shijian)" />
        <van-cell title="结束时间" :value="formatDateTime(detail.jieshu_shijian)" />
        <van-cell title="请假天数" :value="`${detail.qingjia_tianshu} 天`" />
        <van-cell title="审核状态">
          <template #value>
            <van-tag :type="getStatusType(detail.shenhe_zhuangtai!)">
              {{ getStatusText(detail.shenhe_zhuangtai!) }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 请假原因 -->
      <van-cell-group inset title="请假原因">
        <van-cell>
          <div class="reason-content">{{ detail.qingjia_yuanyin }}</div>
        </van-cell>
      </van-cell-group>

      <!-- 附件 -->
      <van-cell-group v-if="attachments.length > 0" inset title="附件">
        <van-cell v-for="(file, index) in attachments" :key="index" :title="`附件${index + 1}`">
          <template #value>
            <van-button size="small" type="primary" @click="downloadFile(file)">
              下载
            </van-button>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 备注 -->
      <van-cell-group v-if="detail.beizhu" inset title="备注">
        <van-cell>
          <div class="remark-content">{{ detail.beizhu }}</div>
        </van-cell>
      </van-cell-group>

      <!-- 审批流程 -->
      <ApprovalWorkflow
        v-if="detail.shenhe_liucheng_id"
        :workflow-id="detail.shenhe_liucheng_id"
      />

      <!-- 操作按钮 -->
      <div v-if="showActions" class="action-buttons">
        <van-button
          v-if="canSubmit"
          round
          block
          type="primary"
          @click="onSubmit"
        >
          提交审批
        </van-button>
        <van-button
          v-if="canApprove"
          round
          block
          type="success"
          @click="onApprove"
        >
          审批通过
        </van-button>
        <van-button
          v-if="canApprove"
          round
          block
          type="danger"
          @click="onReject"
        >
          审批拒绝
        </van-button>
        <van-button
          v-if="canDelete"
          round
          block
          type="danger"
          plain
          @click="onDelete"
        >
          删除
        </van-button>
      </div>
    </div>

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
import { showToast, showConfirmDialog } from 'vant'
import {
  getLeaveDetail,
  submitLeave,
  approveLeave,
  rejectLeave,
  deleteLeave,
  type LeaveApplication
} from '@/api/office'
import { useUserStore } from '@/stores/user'
import ApprovalWorkflow from '@/components/office/ApprovalWorkflow.vue'
import ApprovalDialog from '@/components/office/ApprovalDialog.vue'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const leaveId = computed(() => route.params.id as string)

const loading = ref(false)
const detail = ref<LeaveApplication>({} as LeaveApplication)
const approvalDialogVisible = ref(false)
const approvalAction = ref<'tongguo' | 'jujue'>('tongguo')

// 附件列表
const attachments = computed(() => {
  if (!detail.value.fujian_lujing) return []
  return detail.value.fujian_lujing.split(',').filter(Boolean)
})

// 是否可以编辑
const canEdit = computed(() => {
  return detail.value.shenhe_zhuangtai === 'daishehe'
})

// 是否可以提交
const canSubmit = computed(() => {
  return detail.value.shenhe_zhuangtai === 'daishehe'
})

// 是否可以审批
const canApprove = computed(() => {
  // 检查审批权限
  const hasPermission = userStore.hasPermission('office:qingjia:approve')
  // 检查审核状态
  const isPending = detail.value.shenhe_zhuangtai === 'pending' || detail.value.shenhe_zhuangtai === 'shenhezhong'
  return hasPermission && isPending
})

// 是否可以删除
const canDelete = computed(() => {
  return detail.value.shenhe_zhuangtai === 'daishehe'
})

// 是否显示操作按钮
const showActions = computed(() => {
  return canSubmit.value || canApprove.value || canDelete.value
})

// 加载详情
const loadDetail = async () => {
  loading.value = true
  try {
    detail.value = await getLeaveDetail(leaveId.value)
  } catch (error) {
    console.error('Load leave detail error:', error)
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

// 提交审批
const onSubmit = async () => {
  try {
    await showConfirmDialog({
      title: '确认提交',
      message: '确定要提交审批吗？'
    })

    await submitLeave(leaveId.value)
    showToast('提交成功')
    loadDetail()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Submit error:', error)
    }
  }
}

// 审批通过
const onApprove = () => {
  approvalAction.value = 'tongguo'
  approvalDialogVisible.value = true
}

// 审批拒绝
const onReject = () => {
  approvalAction.value = 'jujue'
  approvalDialogVisible.value = true
}

// 处理审批提交
const handleApprovalSubmit = async (data: { shenhe_jieguo: string; shenhe_yijian: string }) => {
  try {
    if (data.shenhe_jieguo === 'tongguo') {
      await approveLeave(leaveId.value, data.shenhe_yijian)
      showToast('审批通过')
    } else {
      await rejectLeave(leaveId.value, data.shenhe_yijian)
      showToast('已拒绝')
    }

    approvalDialogVisible.value = false
    loadDetail()
  } catch (error) {
    console.error('Approval error:', error)
  }
}

// 删除
const onDelete = async () => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要删除这条请假申请吗？'
    })

    await deleteLeave(leaveId.value)
    showToast('删除成功')
    router.back()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
    }
  }
}

// 跳转到编辑
const goToEdit = () => {
  router.push(`/office/leave/edit/${leaveId.value}`)
}

// 下载文件
const downloadFile = (url: string) => {
  window.open(url, '_blank')
}

// 返回
const onBack = () => {
  router.back()
}

// 获取请假类型文本
const getLeaveTypeText = (type: string) => {
  const map: Record<string, string> = {
    shijia: '事假',
    bingjia: '病假',
    nianjia: '年假',
    tiaoxiu: '调休',
    hunjia: '婚假',
    chanjia: '产假',
    peichanjia: '陪产假',
    sangjia: '丧假'
  }
  return map[type] || type
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daishehe: 'default',
    shenhezhong: 'primary',
    tongguo: 'success',
    jujue: 'danger'
  }
  return map[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    daishehe: '待审核',
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝'
  }
  return map[status] || status
}

// 格式化日期时间
const formatDateTime = (datetime: string) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.leave-detail-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 80px;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.reason-content,
.remark-content {
  padding: 12px 0;
  line-height: 1.6;
  color: #323233;
  white-space: pre-wrap;
}

.action-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background-color: #fff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>

