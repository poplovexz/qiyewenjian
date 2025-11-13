<template>
  <div class="payment-method-form">
    <div class="page-header">
      <h1>{{ isEdit ? '编辑支付方式' : '新建支付方式' }}</h1>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      style="max-width: 600px"
    >
      <el-form-item label="乙方主体" prop="yifang_zhuti_id">
        <el-select
          v-model="form.yifang_zhuti_id"
          placeholder="请选择乙方主体"
          style="width: 100%"
          filterable
        >
          <el-option
            v-for="party in contractParties"
            :key="party.id"
            :label="party.zhuti_mingcheng"
            :value="party.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="支付方式" prop="zhifu_leixing">
        <el-select
          v-model="form.zhifu_leixing"
          placeholder="请选择支付方式"
          style="width: 100%"
        >
          <el-option label="银行转账" value="yinhangzhuanzhang" />
          <el-option label="微信支付" value="weixin" />
          <el-option label="支付宝" value="zhifubao" />
          <el-option label="现金" value="xianjin" />
          <el-option label="其他" value="qita" />
        </el-select>
      </el-form-item>

      <el-form-item label="支付名称" prop="zhifu_mingcheng">
        <el-input
          v-model="form.zhifu_mingcheng"
          placeholder="请输入支付方式名称"
        />
      </el-form-item>

      <el-form-item label="账户名称" prop="zhanghu_mingcheng">
        <el-input
          v-model="form.zhanghu_mingcheng"
          placeholder="请输入账户名称"
        />
      </el-form-item>

      <el-form-item
        v-if="form.zhifu_leixing === 'yinhangzhuanzhang'"
        label="账户号码"
        prop="zhanghu_haoma"
      >
        <el-input
          v-model="form.zhanghu_haoma"
          placeholder="请输入银行账户号码"
        />
      </el-form-item>

      <!-- 银行转账专用字段 -->
      <el-form-item
        v-if="form.zhifu_leixing === 'yinhangzhuanzhang'"
        label="开户行"
        prop="kaihuhang_mingcheng"
      >
        <el-input
          v-model="form.kaihuhang_mingcheng"
          placeholder="请输入开户行"
        />
      </el-form-item>

      <el-form-item
        v-if="form.zhifu_leixing === 'yinhangzhuanzhang'"
        label="联行号"
      >
        <el-input
          v-model="form.lianhang_hao"
          placeholder="请输入联行号（可选）"
        />
      </el-form-item>

      <!-- 微信支付专用字段 -->
      <el-form-item
        v-if="form.zhifu_leixing === 'weixin'"
        label="微信号"
        prop="weixin_haoma"
      >
        <el-input
          v-model="form.weixin_haoma"
          placeholder="请输入微信号或微信收款账号"
        />
      </el-form-item>

      <el-form-item
        v-if="form.zhifu_leixing === 'weixin'"
        label="微信收款名"
      >
        <el-input
          v-model="form.weixin_shoukuan_ming"
          placeholder="请输入微信收款名（可选）"
        />
      </el-form-item>

      <!-- 支付宝专用字段 -->
      <el-form-item
        v-if="form.zhifu_leixing === 'zhifubao'"
        label="支付宝账号"
        prop="zhifubao_haoma"
      >
        <el-input
          v-model="form.zhifubao_haoma"
          placeholder="请输入支付宝账号（手机号或邮箱）"
        />
      </el-form-item>

      <el-form-item
        v-if="form.zhifu_leixing === 'zhifubao'"
        label="支付宝收款名"
      >
        <el-input
          v-model="form.zhifubao_shoukuan_ming"
          placeholder="请输入支付宝收款名（可选）"
        />
      </el-form-item>

      <!-- 微信/支付宝收款码 -->
      <el-form-item
        v-if="form.zhifu_leixing === 'weixin' || form.zhifu_leixing === 'zhifubao'"
        label="收款二维码"
      >
        <el-upload
          class="qrcode-uploader"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          :on-success="handleQrcodeSuccess"
          :before-upload="beforeQrcodeUpload"
          accept="image/*"
        >
          <img v-if="form.erweima_lujing" :src="form.erweima_lujing" class="qrcode-image" />
          <el-icon v-else class="qrcode-uploader-icon"><Plus /></el-icon>
        </el-upload>
        <div class="upload-tip">建议上传清晰的收款二维码图片，支持 JPG、PNG 格式</div>
      </el-form-item>

      <el-form-item label="是否默认">
        <el-switch
          v-model="form.shi_moren"
          active-text="是"
          inactive-text="否"
        />
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group v-model="form.zhifu_zhuangtai">
          <el-radio value="active">启用</el-radio>
          <el-radio value="inactive">停用</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="form.beizhu"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息（可选）"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
        <el-button @click="handleCancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules, type UploadProps } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { useAuthStore } from '@/stores/modules/auth'
import type { PaymentMethodCreate, PaymentMethodUpdate, ContractParty } from '@/api/modules/contract'

const route = useRoute()
const router = useRouter()
const contractStore = useContractManagementStore()
const authStore = useAuthStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const contractParties = ref<ContractParty[]>([])

// 是否编辑模式
const isEdit = computed(() => !!route.params.id)

// 上传配置
const uploadUrl = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/image`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`
}))

// 表单数据
const form = reactive<PaymentMethodCreate & { id?: string }>({
  yifang_zhuti_id: '',
  zhifu_leixing: 'yinhangzhuanzhang',
  zhifu_mingcheng: '',
  zhanghu_mingcheng: '',
  zhanghu_haoma: '',
  kaihuhang_mingcheng: '',
  lianhang_hao: '',
  weixin_haoma: '',
  weixin_shoukuan_ming: '',
  zhifubao_haoma: '',
  zhifubao_shoukuan_ming: '',
  erweima_lujing: '',
  shi_moren: false,
  zhifu_zhuangtai: 'active',
  beizhu: ''
})

// 表单验证规则
const rules: FormRules = {
  yifang_zhuti_id: [
    { required: true, message: '请选择乙方主体', trigger: 'change' }
  ],
  zhifu_leixing: [
    { required: true, message: '请选择支付方式', trigger: 'change' }
  ],
  zhifu_mingcheng: [
    { required: true, message: '请输入支付方式名称', trigger: 'blur' },
    { min: 2, max: 100, message: '支付方式名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  zhanghu_mingcheng: [
    { min: 2, max: 100, message: '账户名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  zhanghu_haoma: [
    {
      validator: (rule, value, callback) => {
        if (form.zhifu_leixing === 'yinhangzhuanzhang' && !value) {
          callback(new Error('银行转账时账户号码为必填'))
        } else if (value && (value.length < 5 || value.length > 50)) {
          callback(new Error('账户号码长度在 5 到 50 个字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  kaihuhang_mingcheng: [
    {
      validator: (rule, value, callback) => {
        if (form.zhifu_leixing === 'yinhangzhuanzhang' && !value) {
          callback(new Error('银行转账时开户行为必填'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  weixin_haoma: [
    {
      validator: (rule, value, callback) => {
        if (form.zhifu_leixing === 'weixin' && !value) {
          callback(new Error('微信支付时微信号为必填'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  zhifubao_haoma: [
    {
      validator: (rule, value, callback) => {
        if (form.zhifu_leixing === 'zhifubao' && !value) {
          callback(new Error('支付宝支付时支付宝账号为必填'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载乙方主体列表
const loadContractParties = async () => {
  try {
    const response = await contractStore.fetchParties({ page: 1, size: 1000 })
    contractParties.value = response.items
  } catch (error) {
    ElMessage.error('加载乙方主体列表失败')
  }
}

// 加载支付方式详情（编辑模式）
const loadPaymentMethodDetail = async () => {
  if (!isEdit.value) return
  
  try {
    const id = route.params.id as string
    const paymentMethod = await contractStore.fetchPaymentMethodDetail(id)
    
    // 填充表单数据
    Object.assign(form, paymentMethod)
  } catch (error) {
    ElMessage.error('加载支付方式详情失败')
    router.push('/payment-methods')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      // 更新支付方式
      const updateData: PaymentMethodUpdate = { ...form }
      delete updateData.id
      await contractStore.updatePaymentMethod(route.params.id as string, updateData)
      ElMessage.success('更新成功')
    } else {
      // 创建支付方式
      await contractStore.createPaymentMethod(form)
      ElMessage.success('创建成功')
    }
    
    router.push('/payment-methods')
  } catch (error) {
    if (error !== false) { // 表单验证失败时不显示错误消息
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

// 取消操作
const handleCancel = () => {
  router.push('/payment-methods')
}

// 二维码上传前检查
const beforeQrcodeUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const isImage = rawFile.type.startsWith('image/')
  const isLt5M = rawFile.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 二维码上传成功
const handleQrcodeSuccess: UploadProps['onSuccess'] = (response) => {
  if (response.code === 200 || response.url) {
    form.erweima_lujing = response.url || response.data?.url
    ElMessage.success('二维码上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 初始化
onMounted(async () => {
  await loadContractParties()
  await loadPaymentMethodDetail()
})
</script>

<style scoped>
.payment-method-form {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.qrcode-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.qrcode-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}

.qrcode-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.qrcode-image {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: contain;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style>
