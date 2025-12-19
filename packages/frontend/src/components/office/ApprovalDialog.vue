<template>
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" :before-close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="审批结果" prop="shenhe_jieguo">
        <el-radio-group v-model="form.shenhe_jieguo">
          <el-radio value="tongguo">
            <el-icon color="#67c23a"><CircleCheck /></el-icon>
            通过
          </el-radio>
          <el-radio value="jujue">
            <el-icon color="#f56c6c"><CircleClose /></el-icon>
            拒绝
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="审批意见" prop="shenhe_yijian">
        <el-input
          v-model="form.shenhe_yijian"
          type="textarea"
          :rows="4"
          :placeholder="
            form.shenhe_jieguo === 'jujue' ? '拒绝时必须填写审批意见' : '请输入审批意见（选填）'
          "
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="附件" v-if="showAttachment">
        <el-upload
          ref="uploadRef"
          :action="uploadAction"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :file-list="fileList"
          :limit="3"
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        >
          <el-button size="small" type="primary">
            <el-icon><Upload /></el-icon>
            上传附件
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF、图片、Word 格式，单个文件不超过 10MB，最多3个文件
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting"> 确定 </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck, CircleClose, Upload } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadProps, UploadUserFile } from 'element-plus'
import { useAuthStore } from '@/stores/modules/auth'

interface Props {
  visible: boolean
  title?: string
  showAttachment?: boolean
  defaultAction?: 'tongguo' | 'jujue'
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '审批操作',
  showAttachment: false,
  defaultAction: 'tongguo',
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  submit: [data: { shenhe_jieguo: string; shenhe_yijian: string; fujian_lujing?: string }]
}>()

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const uploadRef = ref()
const submitting = ref(false)
const fileList = ref<UploadUserFile[]>([])

const form = reactive({
  shenhe_jieguo: props.defaultAction,
  shenhe_yijian: '',
  fujian_lujing: '',
})

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

const dialogTitle = computed(() => {
  if (form.shenhe_jieguo === 'tongguo') {
    return '审批通过'
  } else if (form.shenhe_jieguo === 'jujue') {
    return '审批拒绝'
  }
  return props.title
})

// 表单验证规则
const rules: FormRules = {
  shenhe_jieguo: [{ required: true, message: '请选择审批结果', trigger: 'change' }],
  shenhe_yijian: [
    {
      validator: (rule, value, callback) => {
        if (form.shenhe_jieguo === 'jujue' && !value) {
          callback(new Error('拒绝时必须填写审批意见'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 上传配置
const uploadAction = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/file`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`,
}))

// 监听 visible 变化，重置表单
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      form.shenhe_jieguo = props.defaultAction
      form.shenhe_yijian = ''
      form.fujian_lujing = ''
      fileList.value = []
      formRef.value?.clearValidate()
    }
  }
)

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const allowedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ]
  const isAllowedType = allowedTypes.includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isAllowedType) {
    ElMessage.error('只能上传 PDF、图片、Word 格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

// 上传成功
const handleUploadSuccess: UploadProps['onSuccess'] = (response, file, fileList) => {
  if (response.url) {
    const urls = fileList.map((f) => f.response?.url || f.url).filter(Boolean)
    form.fujian_lujing = urls.join(',')
    ElMessage.success('文件上传成功')
  }
}

// 上传失败
const handleUploadError: UploadProps['onError'] = () => {
  ElMessage.error('文件上传失败')
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitting.value = true

    // 触发提交事件
    emit('submit', {
      shenhe_jieguo: form.shenhe_jieguo,
      shenhe_yijian: form.shenhe_yijian,
      fujian_lujing: form.fujian_lujing,
    })
  } catch (error) {
  } finally {
    submitting.value = false
  }
}

// 关闭
const handleClose = () => {
  dialogVisible.value = false
}

// 暴露方法
defineExpose({
  resetForm: () => {
    formRef.value?.resetFields()
    fileList.value = []
  },
})
</script>

<style scoped lang="scss">
.el-radio {
  display: flex;
  align-items: center;
  margin-right: 30px;

  :deep(.el-radio__label) {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.el-upload__tip {
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}
</style>
