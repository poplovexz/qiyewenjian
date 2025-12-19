<template>
  <div class="contract-sign-page">
    <div v-if="loading" class="loading-container">
      <el-loading-directive v-loading="true" text="加载中..." />
    </div>

    <div v-else-if="error" class="error-container">
      <el-result icon="error" title="签署链接无效" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="contractInfo" class="sign-container">
      <!-- 合同信息 -->
      <el-card class="contract-info-card">
        <template #header>
          <div class="card-header">
            <h2>合同签署</h2>
            <el-tag v-if="contractInfo.qianshu_zhuangtai === 'yiqianshu'" type="success">
              已签署
            </el-tag>
            <el-tag v-else type="warning">待签署</el-tag>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="合同编号">
            {{ contractInfo.hetong_bianhao }}
          </el-descriptions-item>
          <el-descriptions-item label="合同名称">
            {{ contractInfo.hetong_mingcheng }}
          </el-descriptions-item>
          <el-descriptions-item label="有效期至">
            {{ formatDateTime(contractInfo.youxiao_jieshu) }}
          </el-descriptions-item>
          <el-descriptions-item label="签署状态">
            <el-tag :type="getStatusTagType(contractInfo.qianshu_zhuangtai)">
              {{ getStatusText(contractInfo.qianshu_zhuangtai) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="contractInfo.qianshu_ren_mingcheng" label="签署人">
            {{ contractInfo.qianshu_ren_mingcheng }}
          </el-descriptions-item>
          <el-descriptions-item v-if="contractInfo.qianshu_shijian" label="签署时间">
            {{ formatDateTime(contractInfo.qianshu_shijian) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 合同内容 -->
      <el-card class="contract-content-card">
        <template #header>
          <h3>合同内容</h3>
        </template>
        <div
          class="contract-content"
          v-html="sanitizeContractHtml(contractInfo.hetong_neirong)"
        ></div>
      </el-card>

      <!-- 签署表单 -->
      <el-card v-if="contractInfo.qianshu_zhuangtai === 'daiqianshu'" class="sign-form-card">
        <template #header>
          <h3>电子签署</h3>
        </template>

        <el-form ref="signFormRef" :model="signForm" :rules="signFormRules" label-width="120px">
          <el-form-item label="签署人姓名" prop="qianshu_ren_mingcheng">
            <el-input
              v-model="signForm.qianshu_ren_mingcheng"
              placeholder="请输入您的姓名"
              maxlength="50"
            />
          </el-form-item>

          <el-form-item label="联系电话" prop="qianshu_ren_dianhua">
            <el-input
              v-model="signForm.qianshu_ren_dianhua"
              placeholder="请输入您的联系电话"
              maxlength="20"
            />
          </el-form-item>

          <el-form-item label="电子邮箱" prop="qianshu_ren_youxiang">
            <el-input
              v-model="signForm.qianshu_ren_youxiang"
              placeholder="请输入您的电子邮箱"
              maxlength="100"
            />
          </el-form-item>

          <el-form-item label="电子签名" prop="qianming_tupian">
            <div class="signature-container">
              <canvas
                ref="signatureCanvas"
                class="signature-canvas"
                @mousedown="startDrawing"
                @mousemove="draw"
                @mouseup="stopDrawing"
                @touchstart="startDrawing"
                @touchmove="draw"
                @touchend="stopDrawing"
              ></canvas>
              <div class="signature-actions">
                <el-button size="small" @click="clearSignature">清除</el-button>
                <el-button size="small" type="primary" @click="saveSignature">保存签名</el-button>
              </div>
            </div>
            <div v-if="signForm.qianming_tupian" class="signature-preview">
              <img :src="signForm.qianming_tupian" alt="签名预览" />
            </div>
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="agreeTerms" :disabled="submitting">
              我已仔细阅读并同意上述合同条款，确认进行电子签署
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="!agreeTerms"
              @click="handleSubmitSign"
            >
              确认签署
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 已签署信息 -->
      <el-card v-else-if="contractInfo.qianshu_zhuangtai === 'yiqianshu'" class="signed-info-card">
        <template #header>
          <h3>签署信息</h3>
        </template>

        <el-result icon="success" title="合同签署成功" sub-title="您已成功完成合同的电子签署">
          <template #extra>
            <div class="signed-details">
              <p><strong>签署人：</strong>{{ contractInfo.qianshu_ren_mingcheng }}</p>
              <p><strong>签署时间：</strong>{{ formatDateTime(contractInfo.qianshu_shijian) }}</p>
              <div class="payment-notice">
                <el-alert
                  title="请完成支付"
                  description="合同已签署成功，请点击下方按钮完成支付流程"
                  type="info"
                  show-icon
                  :closable="false"
                />
                <div class="payment-actions">
                  <el-button type="primary" size="large" @click="handlePayment">
                    前往支付
                  </el-button>
                </div>
              </div>
            </div>
          </template>
        </el-result>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { contractSignApi } from '@/api/modules/contract'
import { sanitizeContractHtml } from '@/utils/sanitize'

// 合同信息类型
interface ContractInfo {
  id: string
  hetong_bianhao: string
  hetong_mingcheng: string
  hetong_neirong?: string
  hetong_jine?: number
  qianshu_zhuangtai?: string
}

// 路由
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const error = ref('')
const contractInfo = ref<ContractInfo | null>(null)
const submitting = ref(false)
const agreeTerms = ref(false)

// 表单相关
const signFormRef = ref<FormInstance>()
const signForm = ref({
  qianshu_ren_mingcheng: '',
  qianshu_ren_dianhua: '',
  qianshu_ren_youxiang: '',
  qianming_tupian: '',
})

// 签名画布相关
const signatureCanvas = ref<HTMLCanvasElement>()
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)

// 表单验证规则
const signFormRules: FormRules = {
  qianshu_ren_mingcheng: [{ required: true, message: '请输入签署人姓名', trigger: 'blur' }],
  qianshu_ren_dianhua: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' },
  ],
  qianshu_ren_youxiang: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
  qianming_tupian: [{ required: true, message: '请完成电子签名', trigger: 'change' }],
}

// 方法
const fetchContractInfo = async () => {
  const token = route.params.token as string

  if (!token) {
    error.value = '签署令牌无效'
    loading.value = false
    return
  }

  try {
    const response = await contractSignApi.verifyToken(token)
    contractInfo.value = response.data
  } catch (err: unknown) {
    console.error('获取合同信息失败:', err)
    const axiosError = err as { response?: { data?: { detail?: string } } }
    error.value = axiosError.response?.data?.detail || '获取合同信息失败'
  } finally {
    loading.value = false
  }
}

const initSignatureCanvas = () => {
  nextTick(() => {
    const canvas = signatureCanvas.value
    if (!canvas) return

    canvas.width = 400
    canvas.height = 200

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.strokeStyle = '#000'
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  })
}

const startDrawing = (e: MouseEvent | TouchEvent) => {
  isDrawing.value = true
  const rect = signatureCanvas.value?.getBoundingClientRect()
  if (!rect) return

  if (e instanceof MouseEvent) {
    lastX.value = e.clientX - rect.left
    lastY.value = e.clientY - rect.top
  } else {
    lastX.value = e.touches[0].clientX - rect.left
    lastY.value = e.touches[0].clientY - rect.top
  }
}

const draw = (e: MouseEvent | TouchEvent) => {
  if (!isDrawing.value) return

  const canvas = signatureCanvas.value
  const ctx = canvas?.getContext('2d')
  if (!canvas || !ctx) return

  const rect = canvas.getBoundingClientRect()
  let currentX, currentY

  if (e instanceof MouseEvent) {
    currentX = e.clientX - rect.left
    currentY = e.clientY - rect.top
  } else {
    e.preventDefault()
    currentX = e.touches[0].clientX - rect.left
    currentY = e.touches[0].clientY - rect.top
  }

  ctx.beginPath()
  ctx.moveTo(lastX.value, lastY.value)
  ctx.lineTo(currentX, currentY)
  ctx.stroke()

  lastX.value = currentX
  lastY.value = currentY
}

const stopDrawing = () => {
  isDrawing.value = false
}

const clearSignature = () => {
  const canvas = signatureCanvas.value
  const ctx = canvas?.getContext('2d')
  if (!canvas || !ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  signForm.value.qianming_tupian = ''
}

const saveSignature = () => {
  const canvas = signatureCanvas.value
  if (!canvas) return

  const dataURL = canvas.toDataURL('image/png')
  signForm.value.qianming_tupian = dataURL
  ElMessage.success('签名保存成功')
}

const handleSubmitSign = async () => {
  if (!signFormRef.value) return

  try {
    await signFormRef.value.validate()

    if (!signForm.value.qianming_tupian) {
      ElMessage.error('请完成电子签名')
      return
    }

    await ElMessageBox.confirm('确认提交电子签署？提交后将无法修改。', '确认签署', {
      confirmButtonText: '确认签署',
      cancelButtonText: '取消',
      type: 'warning',
    })

    submitting.value = true

    const token = route.params.token as string
    await contractSignApi.submitSign(token, signForm.value)

    ElMessage.success('合同签署成功！')

    // 重新获取合同信息
    await fetchContractInfo()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      console.error('合同签署失败:', error)
      ElMessage.error('合同签署失败')
    }
  } finally {
    submitting.value = false
  }
}

const handlePayment = () => {
  // 跳转到支付页面
  router.push(`/contract-payment/${contractInfo.value.hetong_id}`)
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    daiqianshu: 'warning',
    yiqianshu: 'success',
    guoqi: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    daiqianshu: '待签署',
    yiqianshu: '已签署',
    guoqi: '已过期',
  }
  return texts[status] || status
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

// 生命周期
onMounted(async () => {
  await fetchContractInfo()
  initSignatureCanvas()
})
</script>

<style scoped>
.contract-sign-page {
  /* 🔧 修复：移除 min-height，让页面自然滚动 */
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: auto; /* 确保可以滚动 */
}

.loading-container,
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.sign-container {
  max-width: 800px;
  margin: 0 auto;
}

.contract-info-card,
.contract-content-card,
.sign-form-card,
.signed-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.contract-content {
  /* 🔧 修复：移除最大高度限制，让内容完整显示 */
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #fafafa;
  line-height: 1.6;
  white-space: pre-wrap; /* 保留换行符 */
  word-wrap: break-word; /* 自动换行 */
}

.signature-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  background-color: #fafafa;
}

.signature-canvas {
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  background-color: white;
  cursor: crosshair;
  display: block;
  margin-bottom: 12px;
}

.signature-actions {
  text-align: right;
}

.signature-preview {
  margin-top: 12px;
  text-align: center;
}

.signature-preview img {
  max-width: 200px;
  max-height: 100px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.signed-details {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.signed-details p {
  margin: 8px 0;
  color: #606266;
}

.payment-notice {
  margin-top: 24px;
}

.payment-actions {
  margin-top: 16px;
  text-align: center;
}

@media (max-width: 768px) {
  .contract-sign-page {
    padding: 10px;
  }

  .sign-container {
    max-width: 100%;
  }

  .signature-canvas {
    width: 100%;
    max-width: 350px;
  }
}
</style>
