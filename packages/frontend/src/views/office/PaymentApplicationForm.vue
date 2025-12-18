<template>
  <div class="payment-form">
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
            <el-form-item label="付款对象" prop="fukuan_duixiang">
              <el-input v-model="form.fukuan_duixiang" placeholder="请输入付款对象名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="付款金额" prop="fukuan_jine">
              <el-input-number
                v-model="form.fukuan_jine"
                :min="0.01"
                :precision="2"
                :controls="false"
                placeholder="请输入付款金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="付款方式" prop="fukuan_fangshi">
              <el-select v-model="form.fukuan_fangshi" placeholder="请选择付款方式" style="width: 100%">
                <el-option label="银行转账" value="yinhang_zhuanzhang" />
                <el-option label="支票" value="zhipiao" />
                <el-option label="现金" value="xianjin" />
                <el-option label="支付宝" value="zhifubao" />
                <el-option label="微信" value="weixin" />
                <el-option label="其他" value="qita" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="要求付款时间" prop="yaoqiu_fukuan_shijian">
              <el-date-picker
                v-model="form.yaoqiu_fukuan_shijian"
                type="date"
                placeholder="选择要求付款时间"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="付款原因" prop="fukuan_yuanyin">
          <el-input
            v-model="form.fukuan_yuanyin"
            type="textarea"
            :rows="4"
            placeholder="请详细说明付款原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 收款信息 -->
        <el-divider content-position="left">收款信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="收款账户" prop="shoukuan_zhanghu">
              <el-input v-model="form.shoukuan_zhanghu" placeholder="请输入收款账户/账号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="收款银行" prop="shoukuan_yinhang">
              <el-input v-model="form.shoukuan_yinhang" placeholder="请输入收款银行（选填）" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 附件上传 -->
        <el-divider content-position="left">附件上传</el-divider>

        <el-form-item label="相关凭证">
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
                支持 PDF、JPG、PNG 格式，单个文件不超过 10MB，最多上传5个文件（如合同、发票等）
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
  getPaymentDetail, 
  createPayment, 
  updatePayment,
  type PaymentApplication 
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

const paymentId = computed(() => route.params.id as string)
const isEdit = computed(() => Boolean(paymentId.value))
const pageTitle = computed(() => isEdit.value ? '编辑对外付款申请' : '新建对外付款申请')

const form = reactive<Partial<PaymentApplication>>({
  fukuan_duixiang: '',
  fukuan_jine: 0,
  fukuan_yuanyin: '',
  fukuan_fangshi: '',
  shoukuan_zhanghu: '',
  shoukuan_yinhang: '',
  yaoqiu_fukuan_shijian: '',
  fujian_lujing: '',
  beizhu: ''
})

const rules: FormRules = {
  fukuan_duixiang: [
    { required: true, message: '请输入付款对象', trigger: 'blur' }
  ],
  fukuan_jine: [
    { required: true, message: '请输入付款金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '付款金额必须大于0', trigger: 'blur' }
  ],
  fukuan_fangshi: [
    { required: true, message: '请选择付款方式', trigger: 'change' }
  ],
  fukuan_yuanyin: [
    { required: true, message: '请输入付款原因', trigger: 'blur' },
    { min: 10, message: '付款原因至少10个字符', trigger: 'blur' }
  ],
  shoukuan_zhanghu: [
    { required: true, message: '请输入收款账户', trigger: 'blur' }
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
    const data = await getPaymentDetail(paymentId.value)
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
    ElMessage.error('获取付款申请详情失败')
    router.push('/office/payment')
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
      await updatePayment(paymentId.value, data)
      ElMessage.success('草稿保存成功')
    } else {
      const result = await createPayment(data)
      ElMessage.success('草稿保存成功')
      router.replace(`/office/payment/edit/${result.id}`)
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
      `确定要${isEdit.value ? '更新' : '创建'}这条付款申请吗？`,
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
      await updatePayment(paymentId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createPayment(data)
      ElMessage.success('创建成功')
    }

    router.push('/office/payment')
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
.payment-form {
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

