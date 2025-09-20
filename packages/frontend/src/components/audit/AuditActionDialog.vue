<template>
  <el-dialog
    v-model="dialogVisible"
    title="审核操作"
    width="600px"
    :before-close="handleClose"
  >
    <div v-if="task" class="audit-action-dialog">
      <!-- 任务信息 -->
      <div class="task-info-section">
        <h4>任务信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="审核类型">
            <el-tag :type="getAuditTypeTagType(task.audit_type)">
              {{ getAuditTypeText(task.audit_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="流程编号">
            {{ task.workflow_number }}
          </el-descriptions-item>
          <el-descriptions-item label="审核步骤">
            {{ task.step_name }}
          </el-descriptions-item>
          <el-descriptions-item label="关联对象">
            {{ task.related_info?.name || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="申请原因" :span="2">
            {{ task.applicant_reason || '无' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 审核表单 -->
      <div class="audit-form-section">
        <h4>审核操作</h4>
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="100px"
        >
          <el-form-item label="审核结果" prop="shenhe_jieguo">
            <el-radio-group v-model="formData.shenhe_jieguo">
              <el-radio value="tongguo">
                <el-icon><Check /></el-icon>
                通过
              </el-radio>
              <el-radio value="jujue">
                <el-icon><Close /></el-icon>
                拒绝
              </el-radio>
              <el-radio value="zhuanfa">
                <el-icon><Share /></el-icon>
                转发
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="审核意见" prop="shenhe_yijian">
            <el-input
              v-model="formData.shenhe_yijian"
              type="textarea"
              :rows="4"
              placeholder="请输入审核意见"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="附件">
            <el-upload
              ref="uploadRef"
              :action="uploadAction"
              :headers="uploadHeaders"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :file-list="fileList"
              :limit="1"
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                上传附件
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、Word、图片格式，文件大小不超过 10MB
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item label="附件描述" v-if="formData.fujian_lujing">
            <el-input
              v-model="formData.fujian_miaoshu"
              placeholder="请输入附件描述"
              maxlength="200"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          提交审核
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadProps } from 'element-plus'
import {
  Check,
  Close,
  Share,
  Upload
} from '@element-plus/icons-vue'
import { useAuditManagementStore } from '@/stores/modules/auditManagement'
import { useAuthStore } from '@/stores/modules/auth'

// Props
interface Props {
  visible: boolean
  task: any
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  task: null
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

// 使用store
const auditStore = useAuditManagementStore()
const authStore = useAuthStore()

// 响应式数据
const formRef = ref<FormInstance>()
const uploadRef = ref()
const submitting = ref(false)
const fileList = ref<any[]>([])

const formData = ref({
  shenhe_jieguo: '',
  shenhe_yijian: '',
  fujian_lujing: '',
  fujian_miaoshu: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const uploadAction = computed(() => {
  return `${import.meta.env.VITE_API_BASE_URL}/api/v1/upload/file`
})

const uploadHeaders = computed(() => {
  const token = authStore.accessToken || localStorage.getItem('access_token') || ''
  return token
    ? {
        Authorization: `Bearer ${token}`
      }
    : {}
})

// 表单验证规则
const formRules: FormRules = {
  shenhe_jieguo: [
    { required: true, message: '请选择审核结果', trigger: 'change' }
  ],
  shenhe_yijian: [
    { required: true, message: '请输入审核意见', trigger: 'blur' }
  ]
}

// 方法
const handleClose = () => {
  resetForm()
  emit('update:visible', false)
}

const resetForm = () => {
  formData.value = {
    shenhe_jieguo: '',
    shenhe_yijian: '',
    fujian_lujing: '',
    fujian_miaoshu: ''
  }
  fileList.value = []
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    await ElMessageBox.confirm(
      '确定要提交此审核结果吗？提交后将无法修改。',
      '确认提交',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitting.value = true

    await auditStore.processAuditAction(
      props.task.workflow_id,
      props.task.step_id,
      formData.value
    )

    emit('success')
    ElMessage.success('审核操作提交成功')

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交审核失败:', error)
      ElMessage.error('提交审核失败')
    }
  } finally {
    submitting.value = false
  }
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isValidType = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/jpg',
    'image/png'
  ].includes(file.type)

  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 PDF、Word、图片格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response: any) => {
  if (response.success) {
    formData.value.fujian_lujing = response.data.file_path
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error('文件上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
}

const getAuditTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    hetong: 'primary',
    baojia: 'success'
  }
  return types[type] || 'info'
}

const getAuditTypeText = (type: string) => {
  const texts: Record<string, string> = {
    hetong: '合同审核',
    baojia: '报价审核'
  }
  return texts[type] || type
}

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
  }
})
</script>

<style scoped>
.audit-action-dialog {
  max-height: 600px;
  overflow-y: auto;
}

.task-info-section,
.audit-form-section {
  margin-bottom: 24px;
}

.task-info-section h4,
.audit-form-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-radio) {
  display: flex;
  align-items: center;
  margin-right: 24px;
  margin-bottom: 12px;
}

:deep(.el-radio__label) {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
