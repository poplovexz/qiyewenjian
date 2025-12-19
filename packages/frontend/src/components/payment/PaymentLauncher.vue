<template>
  <div class="payment-launcher">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>发起支付</span>
          <el-tag v-if="orderInfo" :type="getStatusType(orderInfo.zhifu_zhuangtai)">
            {{ getStatusText(orderInfo.zhifu_zhuangtai) }}
          </el-tag>
        </div>
      </template>

      <div v-if="orderInfo">
        <!-- 订单信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">{{ orderInfo.dingdan_bianhao }}</el-descriptions-item>
          <el-descriptions-item label="订单名称">{{ orderInfo.dingdan_mingcheng }}</el-descriptions-item>
          <el-descriptions-item label="应付金额">
            <span class="amount">¥{{ orderInfo.yingfu_jine }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="支付状态">
            <el-tag :type="getStatusType(orderInfo.zhifu_zhuangtai)">
              {{ getStatusText(orderInfo.zhifu_zhuangtai) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 支付方式选择 -->
        <div v-if="canPay" class="payment-options">
          <el-divider content-position="left">选择支付方式</el-divider>
          
          <el-form :model="paymentForm" label-width="120px">
            <el-form-item label="支付平台">
              <el-radio-group v-model="paymentForm.zhifu_pingtai">
                <el-radio label="weixin">微信支付</el-radio>
                <el-radio label="zhifubao">支付宝</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 微信支付方式 -->
            <el-form-item v-if="paymentForm.zhifu_pingtai === 'weixin'" label="支付方式">
              <el-radio-group v-model="paymentForm.zhifu_fangshi">
                <el-radio label="native">扫码支付</el-radio>
                <el-radio label="h5">H5支付</el-radio>
                <el-radio label="jsapi">公众号支付</el-radio>
                <el-radio label="app">APP支付</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 支付宝支付方式 -->
            <el-form-item v-if="paymentForm.zhifu_pingtai === 'zhifubao'" label="支付方式">
              <el-radio-group v-model="paymentForm.zhifu_fangshi">
                <el-radio label="page">网页支付</el-radio>
                <el-radio label="wap">手机网页支付</el-radio>
                <el-radio label="app">APP支付</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 微信JSAPI需要openid -->
            <el-form-item v-if="paymentForm.zhifu_pingtai === 'weixin' && paymentForm.zhifu_fangshi === 'jsapi'" label="用户OpenID">
              <el-input v-model="paymentForm.openid" placeholder="请输入微信用户OpenID" />
            </el-form-item>

            <!-- 支付宝需要return_url -->
            <el-form-item v-if="paymentForm.zhifu_pingtai === 'zhifubao' && ['page', 'wap'].includes(paymentForm.zhifu_fangshi)" label="返回URL">
              <el-input v-model="paymentForm.return_url" placeholder="支付成功后返回的URL" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleCreatePayment">
                发起支付
              </el-button>
              <el-button @click="handleQueryPayment" :loading="queryLoading">
                查询支付状态
              </el-button>
              <el-button v-if="canClose" type="danger" @click="handleClosePayment">
                关闭订单
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 支付结果展示 -->
        <div v-if="paymentResult" class="payment-result">
          <el-divider content-position="left">支付信息</el-divider>
          
          <!-- 二维码支付 -->
          <div v-if="showQRCode" class="qrcode-container">
            <el-alert
              title="请使用微信扫码支付"
              type="info"
              :closable="false"
              show-icon
            />
            <div class="qrcode">
              <qrcode-vue :value="qrcodeUrl" :size="200" level="H" />
            </div>
            <p class="qrcode-tip">请使用微信扫描二维码完成支付</p>
          </div>

          <!-- 跳转支付 -->
          <div v-else-if="paymentUrl" class="payment-url">
            <el-alert
              title="即将跳转到支付页面"
              type="success"
              :closable="false"
              show-icon
            />
            <el-button type="primary" size="large" @click="handleJumpToPayment">
              前往支付
            </el-button>
          </div>

          <!-- 原始数据 -->
          <el-collapse v-model="activeCollapse">
            <el-collapse-item title="查看原始数据" name="raw">
              <pre>{{ JSON.stringify(paymentResult, null, 2) }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import QrcodeVue from 'qrcode.vue'
import { createPayment, queryPayment, closePayment } from '@/api/modules/payment-api'

// 订单信息类型
interface OrderInfo {
  id: string
  zhifu_zhuangtai: string
  jine: number
}

// 支付结果类型
interface PaymentResult {
  success: boolean
  payment_url?: string
  qr_code?: string
}

interface Props {
  orderId: string
}

const props = defineProps<Props>()

const orderInfo = ref<OrderInfo | null>(null)
const loading = ref(false)
const queryLoading = ref(false)
const paymentResult = ref<PaymentResult | null>(null)
const activeCollapse = ref<string[]>([])

const paymentForm = ref({
  zhifu_pingtai: 'weixin' as 'weixin' | 'zhifubao',
  zhifu_fangshi: 'native' as 'native' | 'jsapi' | 'h5' | 'app',
  openid: '',
  return_url: window.location.origin + '/payment/success',
  quit_url: window.location.origin + '/payment/cancel'
})

// 是否可以支付
const canPay = computed(() => {
  return orderInfo.value && ['pending', 'failed'].includes(orderInfo.value.zhifu_zhuangtai)
})

// 是否可以关闭
const canClose = computed(() => {
  return orderInfo.value && !['paid', 'cancelled'].includes(orderInfo.value.zhifu_zhuangtai)
})

// 是否显示二维码
const showQRCode = computed(() => {
  if (!paymentResult.value) return false
  const data = paymentResult.value.payment_data
  return data && (data.code_url || data.qr_code)
})

// 二维码URL
const qrcodeUrl = computed(() => {
  if (!paymentResult.value) return ''
  const data = paymentResult.value.payment_data
  return data.code_url || data.qr_code || ''
})

// 支付URL
const paymentUrl = computed(() => {
  if (!paymentResult.value) return ''
  const data = paymentResult.value.payment_data
  return data.h5_url || data.mweb_url || data.pay_url || ''
})

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'info',
    paying: 'warning',
    paid: 'success',
    failed: 'danger',
    cancelled: 'info',
    refunded: 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待支付',
    paying: '支付中',
    paid: '已支付',
    failed: '支付失败',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return textMap[status] || status
}

// 加载订单信息
const loadOrderInfo = async () => {
  try {
    // 这里应该调用获取订单详情的API
    // 暂时使用props.orderId作为占位
    // orderInfo.value = await getPaymentOrder(props.orderId)
  } catch (error) {
    ElMessage.error('加载订单信息失败')
  }
}

// 创建支付
const handleCreatePayment = async () => {
  loading.value = true
  try {
    const result = await createPayment({
      dingdan_id: props.orderId,
      zhifu_pingtai: paymentForm.value.zhifu_pingtai,
      zhifu_fangshi: paymentForm.value.zhifu_fangshi,
      openid: paymentForm.value.openid || undefined,
      return_url: paymentForm.value.return_url || undefined,
      quit_url: paymentForm.value.quit_url || undefined
    })
    
    paymentResult.value = result
    ElMessage.success('支付创建成功')
    
    // 如果是跳转支付，自动跳转
    if (paymentUrl.value) {
      setTimeout(() => {
        handleJumpToPayment()
      }, 1000)
    }
  } catch (error: unknown) {
    const axiosError = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(axiosError.response?.data?.detail || '创建支付失败')
  } finally {
    loading.value = false
  }
}

// 查询支付状态
const handleQueryPayment = async () => {
  queryLoading.value = true
  try {
    const result = await queryPayment(props.orderId)
    ElMessage.success('查询成功')

    // 更新订单状态
    if (orderInfo.value) {
      orderInfo.value.zhifu_zhuangtai = result.zhifu_zhuangtai
    }

    // 如果已支付，刷新页面
    if (result.zhifu_zhuangtai === 'paid') {
      ElMessage.success('支付成功！')
      setTimeout(() => {
        window.location.reload()
      }, 1500)
    }
  } catch (error: unknown) {
    const axiosError = error as { response?: { data?: { detail?: string } } }
    ElMessage.error(axiosError.response?.data?.detail || '查询失败')
  } finally {
    queryLoading.value = false
  }
}

// 关闭订单
const handleClosePayment = async () => {
  try {
    await ElMessageBox.confirm('确定要关闭此订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await closePayment(props.orderId)
    ElMessage.success('订单已关闭')

    // 刷新页面
    setTimeout(() => {
      window.location.reload()
    }, 1000)
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const axiosError = error as { response?: { data?: { detail?: string } } }
      ElMessage.error(axiosError.response?.data?.detail || '关闭订单失败')
    }
  }
}

// 跳转到支付页面
const handleJumpToPayment = () => {
  if (paymentUrl.value) {
    window.open(paymentUrl.value, '_blank')
  }
}

onMounted(() => {
  loadOrderInfo()
})
</script>

<style scoped lang="scss">
.payment-launcher {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .amount {
    font-size: 18px;
    font-weight: bold;
    color: #f56c6c;
  }

  .payment-options {
    margin-top: 20px;
  }

  .payment-result {
    margin-top: 20px;

    .qrcode-container {
      text-align: center;
      padding: 20px;

      .qrcode {
        margin: 20px 0;
        display: flex;
        justify-content: center;
      }

      .qrcode-tip {
        color: #909399;
        font-size: 14px;
      }
    }

    .payment-url {
      text-align: center;
      padding: 20px;

      .el-button {
        margin-top: 20px;
      }
    }

    pre {
      background: #f5f7fa;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
    }
  }
}
</style>
