<template>
  <el-dialog
    v-model="visible"
    title="完成工单"
    width="600px"
    @close="handleClose"
  >
    <div v-if="order" class="order-info">
      <h4>工单信息</h4>
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="工单编号">
          {{ order.gongdan_bianhao }}
        </el-descriptions-item>
        <el-descriptions-item label="工单标题">
          {{ order.gongdan_biaoti }}
        </el-descriptions-item>
        <el-descriptions-item label="服务类型">
          {{ serviceOrderStore.serviceTypeMap[order.fuwu_leixing] }}
        </el-descriptions-item>
        <el-descriptions-item label="当前进度">
          <el-progress
            :percentage="order.progress_percentage"
            :color="getProgressColor(order.progress_percentage)"
            :stroke-width="8"
          />
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      style="margin-top: 20px"
    >
      <el-form-item label="完成情况" prop="wancheng_qingkuang">
        <el-input
          v-model="formData.wancheng_qingkuang"
          type="textarea"
          :rows="4"
          placeholder="请详细描述工单完成情况，包括完成的工作内容、遇到的问题及解决方案等"
        />
      </el-form-item>
      
      <el-form-item label="交付文件" prop="jiaofei_wenjian">
        <el-input
          v-model="formData.jiaofei_wenjian"
          type="textarea"
          :rows="2"
          placeholder="请输入交付文件列表，多个文件用逗号分隔（如：财务报表.pdf,纳税申报表.pdf）"
        />
      </el-form-item>
      
      <el-form-item label="文件上传">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          multiple
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="fileList"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 pdf、doc、docx、xls、xlsx 格式文件，单个文件不超过 10MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确认完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useServiceOrderStore, type ServiceOrder } from '@/stores/modules/serviceOrderManagement'

// Props
interface Props {
  visible: boolean
  order: ServiceOrder | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Store
const serviceOrderStore = useServiceOrderStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const fileList = ref<UploadFile[]>([])

const formData = reactive({
  wancheng_qingkuang: '',
  jiaofei_wenjian: ''
})

// 表单验证规则
const formRules: FormRules = {
  wancheng_qingkuang: [
    { required: true, message: '请输入完成情况', trigger: 'blur' },
    { min: 10, message: '完成情况描述至少10个字符', trigger: 'blur' }
  ]
}

// 方法
const getProgressColor = (percentage: number) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const handleFileChange = (file: UploadFile, fileList: UploadFile[]) => {
  // 验证文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  
  if (file.raw && !allowedTypes.includes(file.raw.type)) {
    ElMessage.error('只支持 PDF、Word、Excel 格式文件')
    return false
  }
  
  // 验证文件大小
  if (file.raw && file.raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  // 更新交付文件列表
  const fileNames = fileList.map(f => f.name).join(',')
  formData.jiaofei_wenjian = fileNames
}

const handleSubmit = async () => {
  if (!formRef.value || !props.order) return

  try {
    await formRef.value.validate()
    
    // 确认对话框
    await ElMessageBox.confirm(
      '确认完成此工单？完成后工单状态将变为已完成，无法再次修改。',
      '确认完成',
      {
        type: 'warning',
        confirmButtonText: '确认完成',
        cancelButtonText: '取消'
      }
    )
    
    loading.value = true
    
    await serviceOrderStore.completeServiceOrder(
      props.order.id,
      formData.wancheng_qingkuang,
      formData.jiaofei_wenjian
    )
    
    emit('success')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('完成工单失败:', error)
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  Object.assign(formData, {
    wancheng_qingkuang: '',
    jiaofei_wenjian: ''
  })
  
  fileList.value = []
}

// 监听
watch(() => props.visible, (newVal) => {
  if (newVal && props.order) {
    // 预填充一些默认内容
    formData.wancheng_qingkuang = `${serviceOrderStore.serviceTypeMap[props.order.fuwu_leixing]}服务已完成，具体包括：\n\n1. \n2. \n3. \n\n所有工作均按照标准流程执行，质量符合要求。`
  }
})
</script>

<style scoped>
.order-info {
  margin-bottom: 20px;
}

.order-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.dialog-footer {
  text-align: right;
}

.upload-demo {
  width: 100%;
}
</style>
