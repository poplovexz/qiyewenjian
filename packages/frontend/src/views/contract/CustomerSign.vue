<template>
  <div class="customer-sign-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="50"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        title="签署链接无效"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <!-- 主内容 -->
    <div v-else-if="contractInfo" class="sign-container">
      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps">
        <el-step title="查看合同" />
        <el-step title="电子签名" />
        <el-step title="支付" />
        <el-step title="完成" />
      </el-steps>

      <!-- 步骤1: 查看合同 -->
      <div v-show="currentStep === 0" class="step-content">
        <el-card class="contract-card">
          <template #header>
            <div class="card-header">
              <h2>{{ contractInfo.hetong_mingcheng }}</h2>
              <el-tag type="info">合同编号: {{ contractInfo.hetong_bianhao }}</el-tag>
            </div>
          </template>

          <el-descriptions :column="2" border class="contract-info">
            <el-descriptions-item label="到期日期">
              {{ formatDate(contractInfo.daoqi_riqi) }}
            </el-descriptions-item>
            <el-descriptions-item label="合同金额">
              <span class="amount">¥{{ contractInfo.payment_amount || '待定' }}</span>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">合同内容</el-divider>
          <div class="contract-content" v-html="contractInfo.hetong_neirong"></div>

          <div class="step-actions">
            <el-button type="primary" size="large" @click="nextStep">
              我已阅读，继续签署
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 步骤2: 电子签名 -->
      <div v-show="currentStep === 1" class="step-content">
        <el-card class="sign-card">
          <template #header>
            <h3>电子签名</h3>
          </template>

          <el-form
            ref="signFormRef"
            :model="signForm"
            :rules="signFormRules"
            label-width="120px"
          >
            <el-form-item label="签署人姓名" prop="signer_name">
              <el-input
                v-model="signForm.signer_name"
                placeholder="请输入您的姓名"
                maxlength="50"
              />
            </el-form-item>

            <el-form-item label="联系电话" prop="signer_phone">
              <el-input
                v-model="signForm.signer_phone"
                placeholder="请输入您的联系电话"
                maxlength="20"
              />
            </el-form-item>

            <el-form-item label="电子邮箱" prop="signer_email">
              <el-input
                v-model="signForm.signer_email"
                placeholder="请输入您的电子邮箱"
                maxlength="100"
              />
            </el-form-item>

            <el-form-item label="电子签名" prop="signature_data">
              <div class="signature-container">
                <div class="signature-hint">
                  <el-icon><Edit /></el-icon>
                  请在下方区域内签名
                </div>
                <canvas
                  ref="signatureCanvas"
                  class="signature-canvas"
                  @mousedown="startDrawing"
                  @mousemove="draw"
                  @mouseup="stopDrawing"
                  @mouseleave="stopDrawing"
                  @touchstart.prevent="startDrawing"
                  @touchmove.prevent="draw"
                  @touchend="stopDrawing"
                ></canvas>
                <div class="signature-actions">
                  <el-button size="small" @click="clearSignature">
                    <el-icon><Delete /></el-icon>
                    清除签名
                  </el-button>
                </div>
              </div>
            </el-form-item>
          </el-form>

          <div class="step-actions">
            <el-button size="large" @click="prevStep">上一步</el-button>
            <el-button
              type="primary"
              size="large"
              @click="submitSignature"
              :loading="submitting"
            >
              确认签名
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 步骤3: 支付 -->
      <div v-show="currentStep === 2" class="step-content">
        <el-card class="payment-card">
          <template #header>
            <h3>支付</h3>
          </template>

          <el-alert
            title="签署成功"
            type="success"
            :closable="false"
            style="margin-bottom: 20px"
          >
            您已成功签署合同，请完成支付
          </el-alert>

          <div class="payment-info">
            <div class="amount-display">
              <span class="label">应付金额：</span>
              <span class="amount">¥{{ contractInfo.payment_amount }}</span>
            </div>

            <el-divider />

            <el-form label-width="120px">
              <el-form-item label="支付方式">
                <el-radio-group v-model="paymentMethod" v-loading="loadingPaymentMethods">
                  <el-radio
                    v-for="method in availablePaymentMethods"
                    :key="method.method"
                    :label="method.method"
                  >
                    <el-icon><Money /></el-icon>
                    {{ method.label }}
                    <span class="payment-method-desc">{{ method.description }}</span>
                  </el-radio>
                </el-radio-group>
                <div v-if="availablePaymentMethods.length === 0 && !loadingPaymentMethods" class="no-payment-methods">
                  <el-alert type="warning" :closable="false">
                    暂无可用的在线支付方式，请选择银行转账
                  </el-alert>
                </div>
              </el-form-item>
            </el-form>

            <!-- 银行转账信息 -->
            <div v-if="paymentMethod === 'bank'" class="bank-payment-section">
              <el-alert type="info" :closable="false" class="bank-info-alert">
                <template #title>
                  <h3>公司银行账户信息</h3>
                </template>
                <div class="bank-account-info">
                  <p><strong>收款单位：</strong>XX代理记账服务有限公司</p>
                  <p><strong>开户银行：</strong>中国工商银行北京分行</p>
                  <p><strong>银行账号：</strong>1234 5678 9012 3456 789</p>
                  <p><strong>应付金额：</strong><span class="amount-highlight">¥{{ contractInfo.payment_amount }}</span></p>
                </div>
              </el-alert>

              <el-alert type="warning" :closable="false" style="margin-top: 20px">
                <template #title>
                  <strong>温馨提示</strong>
                </template>
                <ul class="tips-list">
                  <li>请按照以上账户信息进行银行转账</li>
                  <li>转账时请备注合同编号，方便我们核对</li>
                  <li>点击下方"确认使用银行转账"按钮后，我们的业务员会联系您获取汇款凭证</li>
                  <li>财务确认到账后，合同将自动生效</li>
                </ul>
              </el-alert>
            </div>

            <!-- 微信/支付宝二维码 -->
            <div v-if="paymentMethod !== 'bank' && paymentQrCode" class="qr-code-container">
              <QRCode :value="paymentQrCode" :size="250" />
              <p>请使用{{ getPaymentMethodText(paymentMethod) }}扫码支付</p>
              <p class="qr-tip">支付金额：¥{{ contractInfo.payment_amount }}</p>
            </div>
          </div>

          <div class="step-actions">
            <el-button size="large" @click="skipPayment">稍后支付</el-button>
            <el-button
              type="primary"
              size="large"
              @click="initiatePayment"
              :loading="paying"
            >
              {{ paymentMethod === 'bank' ? '确认使用银行转账' : '立即支付' }}
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 步骤4: 完成 -->
      <div v-show="currentStep === 3" class="step-content">
        <el-result
          icon="success"
          title="操作成功"
          :sub-title="paymentCompleted ? '合同已签署并支付成功' : '合同已签署，请尽快完成支付'"
        >
          <template #extra>
            <el-button type="primary" @click="goHome">返回首页</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Money, Edit, Delete } from '@element-plus/icons-vue'
import { request } from '@/utils/request'
import QRCode from '@/components/QRCode.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const error = ref('')
const contractInfo = ref<any>(null)
const currentStep = ref(0)
const submitting = ref(false)
const paying = ref(false)
const paymentCompleted = ref(false)
const paymentMethod = ref('wechat')
const paymentQrCode = ref('')
const availablePaymentMethods = ref<any[]>([])
const loadingPaymentMethods = ref(false)
let paymentStatusTimer: number | null = null

// 签名相关
const signatureCanvas = ref<HTMLCanvasElement>()
const isDrawing = ref(false)
const signFormRef = ref()
const signForm = reactive({
  signer_name: '',
  signer_phone: '',
  signer_email: '',
  signature_data: ''
})

const signFormRules = {
  signer_name: [
    { required: true, message: '请输入签署人姓名', trigger: 'blur' }
  ],
  signer_phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  signer_email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 银行支付不需要表单，客户只需要确认

// 获取签署令牌
const signToken = route.params.token as string

// 加载可用支付方式
const loadAvailablePaymentMethods = async () => {
  try {
    loadingPaymentMethods.value = true
    const response = await request.get(`/contract-sign/sign/${signToken}/available-payment-methods`)
    const data = response.data || response
    availablePaymentMethods.value = data.available_methods || []

    // 设置默认支付方式为第一个可用的在线支付方式
    if (availablePaymentMethods.value.length > 0) {
      const firstOnlineMethod = availablePaymentMethods.value.find(m => m.method !== 'bank')
      paymentMethod.value = firstOnlineMethod ? firstOnlineMethod.method : 'bank'
    }
  } catch (err: any) {
    console.error('加载支付方式失败:', err)
    // 如果加载失败，使用默认支付方式
    availablePaymentMethods.value = [
      { method: 'bank', label: '银行转账', icon: 'bank', description: '通过银行转账支付' }
    ]
    paymentMethod.value = 'bank'
  } finally {
    loadingPaymentMethods.value = false
  }
}

// 加载合同信息
const loadContractInfo = async () => {
  try {
    loading.value = true
    const response = await request.get(`/contract-sign/sign/${signToken}`)
    contractInfo.value = response.data || response

    // 加载可用支付方式
    await loadAvailablePaymentMethods()

    // 如果已经签署，跳到支付步骤
    if (contractInfo.value.signed_at) {
      currentStep.value = 2

      // 如果已经支付成功，直接跳到完成步骤
      if (contractInfo.value.payment_status === 'paid') {
        paymentCompleted.value = true
        currentStep.value = 3
      }
    }
  } catch (err: any) {
    console.error('加载合同信息失败:', err)
    error.value = err.response?.data?.detail || '签署链接无效或已过期'
  } finally {
    loading.value = false
  }
}

// 初始化签名画布
const initCanvas = () => {
  nextTick(() => {
    const canvas = signatureCanvas.value
    if (!canvas) return
    
    canvas.width = canvas.offsetWidth
    canvas.height = 200
    
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.strokeStyle = '#000'
      ctx.lineWidth = 2
      ctx.lineCap = 'round'
    }
  })
}

// 获取鼠标/触摸位置
const getPosition = (e: MouseEvent | TouchEvent, canvas: HTMLCanvasElement) => {
  const rect = canvas.getBoundingClientRect()

  if ('touches' in e) {
    // 触摸事件
    return {
      x: e.touches[0].clientX - rect.left,
      y: e.touches[0].clientY - rect.top
    }
  } else {
    // 鼠标事件
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    }
  }
}

// 开始绘制
const startDrawing = (e: MouseEvent | TouchEvent) => {
  e.preventDefault()
  isDrawing.value = true

  const canvas = signatureCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const pos = getPosition(e, canvas)

  ctx.beginPath()
  ctx.moveTo(pos.x, pos.y)
}

// 绘制
const draw = (e: MouseEvent | TouchEvent) => {
  e.preventDefault()

  if (!isDrawing.value) return

  const canvas = signatureCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const pos = getPosition(e, canvas)

  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
}

// 停止绘制
const stopDrawing = () => {
  isDrawing.value = false
}

// 清除签名
const clearSignature = () => {
  const canvas = signatureCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  signForm.signature_data = ''
}

// 提交签名
const submitSignature = async () => {
  try {
    await signFormRef.value.validate()
    
    const canvas = signatureCanvas.value
    if (!canvas) return
    
    // 获取签名数据
    signForm.signature_data = canvas.toDataURL('image/png')
    
    if (!signForm.signature_data || signForm.signature_data === 'data:,') {
      ElMessage.warning('请先签名')
      return
    }
    
    submitting.value = true
    
    await request.post(`/contract-sign/sign/${signToken}/sign`, signForm)
    
    ElMessage.success('签署成功')
    nextStep()
  } catch (error: any) {
    console.error('签署失败:', error)
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '签署失败')
    }
  } finally {
    submitting.value = false
  }
}

// 发起支付
const initiatePayment = async () => {
  // 检查是否已支付
  if (contractInfo.value.payment_status === 'paid') {
    ElMessage.warning('该合同已支付，无需重复支付')
    paymentCompleted.value = true
    nextStep()
    return
  }

  try {
    paying.value = true

    if (paymentMethod.value === 'bank') {
      // 银行转账：客户只需要确认
      const response = await request.post(
        `/contract-sign/sign/${signToken}/bank-payment`,
        {}  // 空请求体，客户只需确认
      )

      const result = response.data || response
      ElMessage.success(result.message || '已确认使用银行转账，我们的业务员会尽快联系您')
      paymentCompleted.value = false
      nextStep()
    } else {
      // 微信/支付宝：生成二维码
      const response = await request.post(`/contract-sign/sign/${signToken}/pay`, {
        payment_method: paymentMethod.value,
        payment_amount: contractInfo.value.payment_amount
      })

      const paymentInfo = response.data || response
      paymentQrCode.value = paymentInfo.qr_code

      ElMessage.success('支付订单已创建，请扫码支付')

      // 开始轮询支付状态
      startPaymentStatusPolling()
    }
  } catch (error: any) {
    console.error('发起支付失败:', error)
    ElMessage.error(error.response?.data?.detail || '发起支付失败')
  } finally {
    paying.value = false
  }
}

// 开始轮询支付状态
const startPaymentStatusPolling = () => {
  console.log('🔍 开始轮询支付状态...')

  // 清除之前的定时器
  if (paymentStatusTimer) {
    clearInterval(paymentStatusTimer)
  }

  // 每3秒查询一次支付状态
  paymentStatusTimer = window.setInterval(async () => {
    try {
      console.log('🔍 发送支付状态查询请求...')
      const response = await request.get(`/contract-sign/sign/${signToken}/payment-status`, {
        timeout: 30000  // 增加超时时间到30秒
      })
      console.log('🔍 收到支付状态响应:', response)

      const status = response.data || response
      console.log('🔍 解析后的状态:', status)
      console.log('🔍 payment_status 值:', status.payment_status)

      if (status.payment_status === 'paid') {
        console.log('✅ 检测到支付成功！')
        // 支付成功
        stopPaymentStatusPolling()
        paymentCompleted.value = true
        paymentQrCode.value = ''
        currentStep.value = 3  // 直接设置为完成步骤
        ElMessage.success('支付成功！')

        console.log('🔄 已跳转到完成步骤，当前步骤:', currentStep.value)
      } else {
        console.log('⏳ 支付状态:', status.payment_status, '继续轮询...')
      }
    } catch (error) {
      console.error('❌ 查询支付状态失败:', error)
      // 超时错误不停止轮询，继续尝试
      if (error.code !== 'ECONNABORTED') {
        console.error('非超时错误，停止轮询')
        stopPaymentStatusPolling()
      }
    }
  }, 3000)
}

// 停止轮询支付状态
const stopPaymentStatusPolling = () => {
  if (paymentStatusTimer) {
    clearInterval(paymentStatusTimer)
    paymentStatusTimer = null
  }
}

// 跳过支付
const skipPayment = () => {
  stopPaymentStatusPolling()
  paymentCompleted.value = false
  nextStep()
}

// 下一步
const nextStep = () => {
  currentStep.value++

  // 如果进入签名步骤，初始化Canvas
  if (currentStep.value === 1) {
    nextTick(() => {
      initCanvas()
    })
  }
}

// 上一步
const prevStep = () => {
  currentStep.value--
}

// 返回首页
const goHome = () => {
  window.location.href = '/'
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 获取支付方式文本
const getPaymentMethodText = (method: string) => {
  const texts: Record<string, string> = {
    wechat: '微信支付',
    alipay: '支付宝',
    bank: '银行转账'
  }
  return texts[method] || method
}

// 组件挂载
onMounted(() => {
  loadContractInfo()
})

// 组件卸载时清除定时器
onUnmounted(() => {
  stopPaymentStatusPolling()
})
</script>

<style scoped>
.customer-sign-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.sign-container {
  max-width: 1000px;
  margin: 0 auto;
}

.steps {
  margin-bottom: 40px;
  background: white;
  padding: 30px;
  border-radius: 8px;
}

.step-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contract-info {
  margin-bottom: 20px;
}

.contract-content {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #ffffff;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 20px;
  line-height: 1.8;
  font-size: 15px;
  color: #333;
}

.contract-content :deep(h1),
.contract-content :deep(h2),
.contract-content :deep(h3) {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #303133;
}

.contract-content :deep(h1) {
  font-size: 24px;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.contract-content :deep(h2) {
  font-size: 20px;
  color: #409eff;
}

.contract-content :deep(h3) {
  font-size: 18px;
}

.contract-content :deep(p) {
  margin: 10px 0;
}

.contract-content :deep(ul),
.contract-content :deep(ol) {
  margin: 10px 0;
  padding-left: 30px;
}

.contract-content :deep(li) {
  margin: 5px 0;
}

.contract-content :deep(strong) {
  color: #409eff;
  font-weight: 600;
}

.signature-container {
  width: 100%;
  position: relative;
}

.signature-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  margin-bottom: 10px;
  background-color: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  color: #409eff;
  font-size: 14px;
}

.signature-canvas {
  display: block;
  width: 100%;
  height: 200px;
  border: 2px solid #409eff;
  border-radius: 4px;
  cursor: crosshair;
  background-color: #ffffff;
  background-image:
    linear-gradient(to right, #f0f0f0 1px, transparent 1px),
    linear-gradient(to bottom, #f0f0f0 1px, transparent 1px);
  background-size: 20px 20px;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.signature-canvas:hover {
  border-color: #66b1ff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.3);
}

.signature-actions {
  margin-top: 10px;
  text-align: right;
}

.payment-info {
  padding: 20px 0;
}

.amount-display {
  text-align: center;
  padding: 30px 0;
}

.amount-display .label {
  font-size: 18px;
  color: #606266;
}

.amount-display .amount,
.amount {
  font-size: 32px;
  font-weight: bold;
  color: #f56c6c;
  margin-left: 10px;
}

.qr-code-container {
  text-align: center;
  margin-top: 30px;
}

.qr-code {
  width: 200px;
  height: 200px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.step-actions {
  margin-top: 30px;
  text-align: center;
}

.step-actions .el-button {
  min-width: 120px;
  margin: 0 10px;
}

/* 银行支付样式 */
.bank-payment-section {
  margin-top: 20px;
}

.bank-info-alert {
  margin-bottom: 20px;
}

.bank-info-alert h3 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 16px;
}

.bank-account-info {
  line-height: 2;
}

.bank-account-info p {
  margin: 8px 0;
  font-size: 14px;
}

.bank-account-info strong {
  color: #303133;
  margin-right: 8px;
}

.amount-highlight {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}

.bank-payment-form {
  margin-top: 20px;
}

.form-tip {
  color: #909399;
  font-size: 12px;
}

.tips-list {
  margin: 10px 0 0 20px;
  padding: 0;
  list-style: disc;
}

.tips-list li {
  margin: 5px 0;
  color: #e6a23c;
  font-size: 13px;
}

/* 支付方式样式 */
.payment-method-desc {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.no-payment-methods {
  margin-top: 10px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .customer-sign-page {
    padding: 10px;
  }

  .sign-container {
    max-width: 100%;
    padding-bottom: 20px;
  }

  .steps {
    padding: 15px 10px;
    margin-bottom: 20px;
  }

  .step-content {
    margin-top: 15px;
  }

  .contract-content {
    padding: 15px;
    max-height: 400px;
    font-size: 14px;
  }

  .signature-canvas {
    height: 150px;
  }

  .step-actions .el-button {
    min-width: 100px;
    margin: 5px;
  }

  .amount-display .amount,
  .amount {
    font-size: 24px;
  }

  .qr-code {
    width: 150px;
    height: 150px;
  }
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .sign-container {
    max-width: 750px;
  }

  .contract-content {
    max-height: 450px;
  }
}
</style>

<style>
/* 全局样式：确保页面可以滚动 */
html, body {
  overflow-y: auto !important;
  height: auto !important;
  min-height: 100vh !important;
}

/* 确保主容器可以滚动 */
#app {
  min-height: 100vh;
  overflow-y: auto;
}
</style>

