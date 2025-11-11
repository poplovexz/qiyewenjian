<template>
  <div class="reimbursement-form">
    <el-page-header @back="handleBack" :content="pageTitle" />

    <el-card class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="报销类型" prop="baoxiao_leixing">
              <el-select v-model="form.baoxiao_leixing" placeholder="请选择报销类型" style="width: 100%">
                <el-option label="差旅费" value="chailvfei" />
                <el-option label="餐饮费" value="canyinfei" />
                <el-option label="交通费" value="jiaotongfei" />
                <el-option label="办公用品" value="bangongyongpin" />
                <el-option label="其他" value="qita" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报销金额" prop="baoxiao_jine">
              <el-input-number
                v-model="form.baoxiao_jine"
                :min="0.01"
                :precision="2"
                :controls="false"
                placeholder="请输入报销金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="报销事项时间" prop="baoxiao_shijian">
              <el-date-picker
                v-model="form.baoxiao_shijian"
                type="date"
                placeholder="选择报销事项发生时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="报销原因" prop="baoxiao_yuanyin">
          <el-input
            v-model="form.baoxiao_yuanyin"
            type="textarea"
            :rows="4"
            placeholder="请详细说明报销原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 附件上传 -->
        <el-divider content-position="left">附件上传</el-divider>

        <el-form-item label="报销凭证">
          <el-upload
            ref="uploadRef"
            :action="uploadAction"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :file-list="fileList"
            :limit="5"
            accept=".pdf,.jpg,.jpeg,.png"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、JPG、PNG 格式，单个文件不超过 10MB，最多上传5个文件
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- 备注 -->
        <el-divider content-position="left">其他信息</el-divider>

        <el-form-item label="备注">
          <el-input
            v-model="form.beizhu"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button @click="handleBack">取消</el-button>
          <el-button @click="handleSaveDraft" :loading="saving">保存草稿</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadProps, UploadUserFile } from 'element-plus'
import { 
  getReimbursementDetail, 
  createReimbursement, 
  updateReimbursement,
  type ReimbursementApplication 
} from '@/api/office'
import { useAuthStore } from '@/stores/modules/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const uploadRef = ref()
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const fileList = ref<UploadUserFile[]>([])

const reimbursementId = computed(() => route.params.id as string)
const isEdit = computed(() => !!reimbursementId.value)
const pageTitle = computed(() => isEdit.value ? '编辑报销申请' : '新建报销申请')

const form = reactive<Partial<ReimbursementApplication>>({
  baoxiao_leixing: '',
  baoxiao_jine: 0,
  baoxiao_shijian: '',
  baoxiao_yuanyin: '',
  fujian_lujing: '',
  beizhu: ''
})

const rules: FormRules = {
  baoxiao_leixing: [
    { required: true, message: '请选择报销类型', trigger: 'change' }
  ],
  baoxiao_jine: [
    { required: true, message: '请输入报销金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '报销金额必须大于0', trigger: 'blur' }
  ],
  baoxiao_shijian: [
    { required: true, message: '请选择报销事项发生时间', trigger: 'change' }
  ],
  baoxiao_yuanyin: [
    { required: true, message: '请输入报销原因', trigger: 'blur' },
    { min: 10, message: '报销原因至少10个字符', trigger: 'blur' }
  ]
}

// 上传配置
const uploadAction = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/file`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`
}))

// 获取详情（编辑模式）
const fetchDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getReimbursementDetail(reimbursementId.value)
    Object.assign(form, data)
    
    // 处理附件列表
    if (data.fujian_lujing) {
      const files = data.fujian_lujing.split(',').filter(Boolean)
      fileList.value = files.map((url, index) => ({
        name: `附件${index + 1}`,
        url: url
      }))
    }
  } catch (error) {
    ElMessage.error('获取报销申请详情失败')
    router.push('/office/reimbursement')
  } finally {
    loading.value = false
  }
}

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
  const isAllowedType = allowedTypes.includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isAllowedType) {
    ElMessage.error('只能上传 PDF、JPG、PNG 格式的文件!')
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
    // 更新附件路径
    const urls = fileList.map(f => f.response?.url || f.url).filter(Boolean)
    form.fujian_lujing = urls.join(',')
    ElMessage.success('文件上传成功')
  }
}

// 上传失败
const handleUploadError: UploadProps['onError'] = () => {
  ElMessage.error('文件上传失败')
}

// 保存草稿
const handleSaveDraft = async () => {
  saving.value = true
  try {
    const data = { ...form }
    
    if (isEdit.value) {
      await updateReimbursement(reimbursementId.value, data)
      ElMessage.success('草稿保存成功')
    } else {
      const result = await createReimbursement(data)
      ElMessage.success('草稿保存成功')
      // 保存后切换到编辑模式
      router.replace(`/office/reimbursement/edit/${result.id}`)
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    await ElMessageBox.confirm(
      `确定要${isEdit.value ? '更新' : '创建'}这条报销申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitting.value = true
    const data = { ...form }

    if (isEdit.value) {
      await updateReimbursement(reimbursementId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createReimbursement(data)
      ElMessage.success('创建成功')
    }

    router.push('/office/reimbursement')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

// 返回
const handleBack = () => {
  router.back()
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped lang="scss">
.reimbursement-form {
  padding: 20px;

  .form-card {
    margin-top: 20px;
  }

  .el-upload__tip {
    color: #999;
    font-size: 12px;
    margin-top: 8px;
  }
}
</style>

