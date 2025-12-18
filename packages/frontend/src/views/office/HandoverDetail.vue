<template>
  <div class="handover-detail">
    <el-page-header @back="handleBack" content="工作交接单详情" />

    <el-card class="detail-card" v-loading="loading">
      <!-- 基本信息 -->
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="交接编号">
          {{ detail.jiaojie_bianhao }}
        </el-descriptions-item>
        <el-descriptions-item label="交接人">
          {{ detail.jiaojie_ren_xingming }}
        </el-descriptions-item>
        <el-descriptions-item label="接收人">
          {{ detail.jieshou_ren_xingming }}
        </el-descriptions-item>
        <el-descriptions-item label="交接原因">
          <el-tag>{{ getReasonLabel(detail.jiaojie_yuanyin) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="交接时间">
          {{ formatDateTime(detail.jiaojie_shijian) }}
        </el-descriptions-item>
        <el-descriptions-item label="交接状态">
          <el-tag :type="getStatusType(detail.jiaojie_zhuangtai)">
            {{ getStatusLabel(detail.jiaojie_zhuangtai) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 交接内容 -->
      <el-divider content-position="left">交接内容</el-divider>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="工作内容">
          <div class="content-text">{{ detail.jiaojie_neirong }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="文件清单" v-if="detail.wenjian_qingdan">
          <div class="content-text">{{ detail.wenjian_qingdan }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="设备清单" v-if="detail.shebei_qingdan">
          <div class="content-text">{{ detail.shebei_qingdan }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="账号清单" v-if="detail.zhanghu_qingdan">
          <div class="content-text">{{ detail.zhanghu_qingdan }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="待办事项" v-if="detail.daiban_shixiang">
          <div class="content-text">{{ detail.daiban_shixiang }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 确认信息 -->
      <el-divider content-position="left">确认信息</el-divider>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="确认人" v-if="detail.queren_ren_xingming">
          {{ detail.queren_ren_xingming }}
        </el-descriptions-item>
        <el-descriptions-item label="确认时间" v-if="detail.queren_shijian">
          {{ formatDateTime(detail.queren_shijian) }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 其他信息 -->
      <el-divider content-position="left">其他信息</el-divider>
      <el-descriptions :column="2" border>
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
          <el-link :href="file" target="_blank" rel="noopener noreferrer" type="primary">
            <el-icon><Document /></el-icon>
            附件{{ index + 1 }}
          </el-link>
        </div>
      </div>
      <el-empty v-else description="暂无附件" :image-size="80" />

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
          @click="handleSubmitConfirm"
        >
          提交确认
        </el-button>
        <el-button 
          v-if="canConfirm" 
          type="success" 
          @click="handleConfirm"
        >
          确认接收
        </el-button>
        <el-button 
          v-if="canConfirm" 
          type="danger" 
          @click="handleReject"
        >
          拒绝接收
        </el-button>
      </div>
    </el-card>

    <!-- 确认对话框 -->
    <el-dialog v-model="confirmDialogVisible" title="确认操作" width="500px">
      <el-form :model="confirmForm" label-width="100px">
        <el-form-item label="确认结果">
          <el-radio-group v-model="confirmForm.jieguo">
            <el-radio value="queren">确认接收</el-radio>
            <el-radio value="jujue">拒绝接收</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="confirmForm.beizhu"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="confirmDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitConfirm" :loading="confirming">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import {
  getHandoverDetail,
  submitHandoverForConfirm,
  confirmHandover,
  rejectHandover,
  type HandoverApplication
} from '@/api/office'
import { useAuthStore } from '@/stores/modules/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const confirming = ref(false)
const confirmDialogVisible = ref(false)
const detail = ref<Partial<HandoverApplication>>({})

const handoverId = computed(() => route.params.id as string)
const attachments = computed(() => {
  if (!detail.value.fujian_lujing) return []
  return detail.value.fujian_lujing.split(',').filter(Boolean)
})

const canEdit = computed(() => {
  return detail.value.jiaojie_zhuangtai === 'daiqueren'
})

const canSubmit = computed(() => {
  return detail.value.jiaojie_zhuangtai === 'daiqueren'
})

const canConfirm = computed(() => {
  // TODO: 根据实际权限判断（是否为接收人）
  return detail.value.jiaojie_zhuangtai === 'daiqueren' && 
         detail.value.jieshou_ren_id === authStore.user?.id
})

const confirmForm = reactive({
  jieguo: 'queren',
  beizhu: ''
})

// 获取详情
const fetchDetail = async () => {
  loading.value = true
  try {
    const data = await getHandoverDetail(handoverId.value)
    detail.value = data
  } catch (error) {
    ElMessage.error('获取详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 编辑
const handleEdit = () => {
  router.push(`/office/handover/edit/${handoverId.value}`)
}

// 提交确认
const handleSubmitConfirm = async () => {
  try {
    await ElMessageBox.confirm('确定要提交确认吗？', '确认操作', {
      type: 'warning'
    })
    
    await submitHandoverForConfirm(handoverId.value)
    ElMessage.success('提交成功')
    fetchDetail()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  }
}

// 确认接收
const handleConfirm = () => {
  confirmForm.jieguo = 'queren'
  confirmForm.beizhu = ''
  confirmDialogVisible.value = true
}

// 拒绝接收
const handleReject = () => {
  confirmForm.jieguo = 'jujue'
  confirmForm.beizhu = ''
  confirmDialogVisible.value = true
}

// 提交确认结果
const submitConfirm = async () => {
  if (!confirmForm.beizhu && confirmForm.jieguo === 'jujue') {
    ElMessage.warning('拒绝时必须填写备注')
    return
  }

  confirming.value = true
  try {
    if (confirmForm.jieguo === 'queren') {
      await confirmHandover(handoverId.value, confirmForm.beizhu)
      ElMessage.success('已确认接收')
    } else {
      await rejectHandover(handoverId.value, confirmForm.beizhu)
      ElMessage.success('已拒绝接收')
    }
    
    confirmDialogVisible.value = false
    fetchDetail()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    confirming.value = false
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 辅助函数
const getReasonLabel = (reason: string) => {
  const map: Record<string, string> = {
    lizhi: '离职',
    diaogang: '调岗',
    xiujia: '休假',
    qita: '其他'
  }
  return map[reason] || reason
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    daiqueren: '待确认',
    yiqueren: '已确认',
    yijujue: '已拒绝'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    daiqueren: 'warning',
    yiqueren: 'success',
    yijujue: 'danger'
  }
  return map[status] || 'info'
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
.handover-detail {
  padding: 20px;

  .detail-card {
    margin-top: 20px;
  }

  .content-text {
    white-space: pre-wrap;
    line-height: 1.6;
  }

  .attachments {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;

    .attachment-item {
      padding: 10px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      background-color: #f5f7fa;

      &:hover {
        background-color: #ecf5ff;
        border-color: #409eff;
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

