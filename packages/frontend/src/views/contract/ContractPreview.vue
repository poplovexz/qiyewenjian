<template>
  <div class="contract-preview">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合同预览</span>
          <div class="header-actions">
            <el-button @click="handleBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <el-button v-if="canEdit" type="primary" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button v-if="canSign" type="success" @click="handleSign">
              <el-icon><EditPen /></el-icon>
              签署合同
            </el-button>
          </div>
        </div>
      </template>

      <!-- 合同基本信息 -->
      <div class="contract-info" v-if="contract">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="合同编号">
            {{ contract.hetong_bianhao }}
          </el-descriptions-item>
          <el-descriptions-item label="合同名称">
            {{ contract.hetong_mingcheng }}
          </el-descriptions-item>
          <el-descriptions-item label="合同类型">
            {{ getContractTypeLabel(contract.hetong_leixing) }}
          </el-descriptions-item>
          <el-descriptions-item label="合同状态">
            <el-tag :type="getStatusTagType(contract.hetong_zhuangtai)">
              {{ getContractStatusLabel(contract.hetong_zhuangtai) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="合同金额">
            <span class="amount">{{ formatAmount(contract.hetong_jine) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(contract.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="签署日期" v-if="contract.qianding_riqi">
            {{ formatDate(contract.qianding_riqi) }}
          </el-descriptions-item>
          <el-descriptions-item label="生效日期" v-if="contract.shengxiao_riqi">
            {{ formatDate(contract.shengxiao_riqi) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期" v-if="contract.jieshu_riqi">
            {{ formatDate(contract.jieshu_riqi) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 审核流程信息 -->
      <div class="audit-flow-section" v-if="contract && auditHistory.length > 0">
        <h3>审核流程</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(audit, index) in auditHistory"
            :key="audit.id"
            :timestamp="formatDateTime(audit.created_at)"
            :type="getAuditTimelineType(audit.shenhe_zhuangtai)"
            :icon="getAuditTimelineIcon(audit.shenhe_zhuangtai)"
          >
            <el-card class="audit-card">
              <div class="audit-header">
                <span class="audit-title">{{ audit.liucheng_bianhao }}</span>
                <el-tag :type="getAuditStatusTagType(audit.shenhe_zhuangtai)" size="small">
                  {{ getAuditStatusText(audit.shenhe_zhuangtai) }}
                </el-tag>
              </div>
              <div class="audit-content">
                <p><strong>审核类型：</strong>{{ getAuditTypeText(audit.shenhe_leixing) }}</p>
                <p><strong>申请人：</strong>{{ audit.shenqing_ren_mingcheng }}</p>
                <p v-if="audit.shenqing_yuanyin">
                  <strong>申请原因：</strong>{{ audit.shenqing_yuanyin }}
                </p>
                <p v-if="audit.wancheng_shijian">
                  <strong>完成时间：</strong>{{ formatDateTime(audit.wancheng_shijian) }}
                </p>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 签署状态 -->
      <div class="signing-status-section" v-if="contract">
        <h3>签署状态</h3>
        <el-card>
          <div v-if="signingInfo" class="signing-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="签署状态">
                <el-tag :type="getSigningStatusTagType(signingInfo.qianshu_zhuangtai)">
                  {{ getSigningStatusText(signingInfo.qianshu_zhuangtai) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="签署链接" v-if="signingInfo.qianshu_lianjie">
                <el-link
                  :href="signingInfo.qianshu_lianjie"
                  target="_blank"
                  rel="noopener noreferrer"
                  type="primary"
                >
                  查看签署链接
                </el-link>
              </el-descriptions-item>
              <el-descriptions-item label="签署人" v-if="signingInfo.qianshu_ren_mingcheng">
                {{ signingInfo.qianshu_ren_mingcheng }}
              </el-descriptions-item>
              <el-descriptions-item label="签署时间" v-if="signingInfo.qianshu_shijian">
                {{ formatDateTime(signingInfo.qianshu_shijian) }}
              </el-descriptions-item>
              <el-descriptions-item label="有效期至" v-if="signingInfo.youxiao_jieshu">
                {{ formatDateTime(signingInfo.youxiao_jieshu) }}
              </el-descriptions-item>
            </el-descriptions>

            <div v-if="signingInfo.qianshu_zhuangtai === 'daiqianshu'" class="signing-actions">
              <el-button type="primary" @click="handleCreateSigningLink"> 创建签署链接 </el-button>
              <el-button @click="handleCancelSigning"> 取消签署 </el-button>
            </div>
          </div>
          <div v-else class="no-signing-info">
            <el-empty description="暂无签署信息">
              <el-button type="primary" @click="handleCreateSigningLink"> 创建签署链接 </el-button>
            </el-empty>
          </div>
        </el-card>
      </div>

      <!-- 支付状态 -->
      <div class="payment-status-section" v-if="contract">
        <h3>支付状态</h3>
        <el-card>
          <div v-if="paymentInfo && paymentInfo.length > 0" class="payment-info">
            <el-table :data="paymentInfo" style="width: 100%">
              <el-table-column prop="zhifu_fangshi" label="支付方式" width="120">
                <template #default="{ row }">
                  {{ getPaymentMethodText(row.zhifu_fangshi) }}
                </template>
              </el-table-column>
              <el-table-column prop="zhifu_jine" label="支付金额" width="120">
                <template #default="{ row }">
                  {{ formatAmount(row.zhifu_jine) }}
                </template>
              </el-table-column>
              <el-table-column prop="zhifu_zhuangtai" label="支付状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="getPaymentStatusTagType(row.zhifu_zhuangtai)">
                    {{ getPaymentStatusText(row.zhifu_zhuangtai) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="zhifu_shijian" label="支付时间" width="180">
                <template #default="{ row }">
                  {{ row.zhifu_shijian ? formatDateTime(row.zhifu_shijian) : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="zhifu_liushui_hao" label="流水号" min-width="150">
                <template #default="{ row }">
                  {{ row.zhifu_liushui_hao || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button
                    v-if="row.zhifu_zhuangtai === 'daizhi'"
                    size="small"
                    type="primary"
                    @click="handlePayment(row)"
                  >
                    去支付
                  </el-button>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>

            <div class="payment-actions">
              <el-button type="primary" @click="handleCreatePayment"> 创建支付订单 </el-button>
            </div>
          </div>
          <div v-else class="no-payment-info">
            <el-empty description="暂无支付信息">
              <el-button type="primary" @click="handleCreatePayment"> 创建支付订单 </el-button>
            </el-empty>
          </div>
        </el-card>
      </div>

      <!-- 合同内容预览 -->
      <div class="contract-content" v-if="contract">
        <h3>合同内容</h3>
        <div class="content-viewer" v-html="sanitizeContractHtml(contract.hetong_neirong)"></div>
      </div>

      <!-- 电子签名 -->
      <div class="signature-section" v-if="contract?.dianziqianming_lujing">
        <h3>电子签名</h3>
        <div class="signature-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="签名时间">
              {{ formatDateTime(contract.qianming_shijian) }}
            </el-descriptions-item>
            <el-descriptions-item label="签名人">
              {{ contract.qianming_ren_id }}
            </el-descriptions-item>
          </el-descriptions>
          <div class="signature-image" v-if="contract.dianziqianming_lujing">
            <img :src="contract.dianziqianming_lujing" alt="电子签名" />
          </div>
        </div>
      </div>
    </el-card>

    <!-- 电子签名对话框 -->
    <el-dialog
      v-model="signDialogVisible"
      title="电子签名"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="signature-dialog">
        <el-tabs v-model="signatureType" type="border-card">
          <el-tab-pane label="手写签名" name="draw">
            <div class="signature-canvas-container">
              <canvas
                ref="signatureCanvas"
                width="500"
                height="200"
                @mousedown="startDrawing"
                @mousemove="draw"
                @mouseup="stopDrawing"
                @mouseleave="stopDrawing"
              ></canvas>
              <div class="canvas-actions">
                <el-button @click="clearSignature">清除</el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="文字签名" name="text">
            <el-input
              v-model="textSignature"
              placeholder="请输入您的姓名作为签名"
              maxlength="20"
              show-word-limit
            />
            <div class="text-signature-preview" v-if="textSignature">
              <span class="signature-text">{{ textSignature }}</span>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="signDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmSignature" :loading="signing">
            确认签署
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, EditPen, Clock, Check, Close, Warning } from '@element-plus/icons-vue'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { useAuditManagementStore } from '@/stores/modules/auditManagement'
import { contractTypeOptions, contractStatusOptions } from '@/api/modules/contract'
import { formatDateTime, formatDate, formatAmount } from '@/utils/format'
import { sanitizeContractHtml } from '@/utils/sanitize'

const route = useRoute()
const router = useRouter()
const contractStore = useContractManagementStore()
const auditStore = useAuditManagementStore()

// 审核历史类型
interface AuditHistoryItem {
  id: string
  shenhe_jieguo: string
  shenhe_yijian?: string
  shenhe_shijian?: string
  shenhe_ren?: string
}

// 签署信息类型
interface SigningInfo {
  id: string
  qianshu_zhuangtai: string
  qianshu_shijian?: string
}

// 支付信息类型
interface PaymentInfoItem {
  id: string
  zhifu_zhuangtai: string
  zhifu_jine?: number
}

// 响应式数据
const contract = computed(() => contractStore.currentContract)
const loading = computed(() => contractStore.contractLoading)
const auditHistory = ref<AuditHistoryItem[]>([])
const signingInfo = ref<SigningInfo | null>(null)
const paymentInfo = ref<PaymentInfoItem[]>([])

// 签名相关
const signDialogVisible = ref(false)
const signatureType = ref('draw')
const textSignature = ref('')
const signing = ref(false)
const signatureCanvas = ref<HTMLCanvasElement>()
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)

// 计算属性
const canEdit = computed(() => {
  return contract.value && ['draft', 'pending_signature'].includes(contract.value.hetong_zhuangtai)
})

const canSign = computed(() => {
  return contract.value && contract.value.hetong_zhuangtai === 'pending_signature'
})

// 方法
const fetchContractDetail = async () => {
  const contractId = route.params.id as string
  if (contractId) {
    try {
      await contractStore.fetchContractDetail(contractId)

      // 并行获取审核历史、签署信息、支付信息
      await Promise.all([
        fetchAuditHistory(contractId),
        fetchSigningInfo(contractId),
        fetchPaymentInfo(contractId),
      ])
    } catch (error) {
      ElMessage.error('获取合同详情失败')
    }
  }
}

const fetchAuditHistory = async (contractId: string) => {
  try {
    const history = await auditStore.fetchAuditHistory('hetong', contractId)
    auditHistory.value = history
  } catch (error) {}
}

const fetchSigningInfo = async (contractId: string) => {
  try {
    const response = await contractSignApi.getByContract(contractId)
    signingInfo.value = response.data
  } catch (error) {}
}

const fetchPaymentInfo = async (contractId: string) => {
  try {
    const response = await contractPaymentApi.getByContract(contractId)
    paymentInfo.value = response.data
  } catch (error) {}
}

const handleBack = () => {
  router.back()
}

const handleEdit = () => {
  if (contract.value) {
    router.push(`/contracts/${contract.value.id}/edit`)
  }
}

const handleSign = () => {
  signDialogVisible.value = true
  nextTick(() => {
    initSignatureCanvas()
  })
}

const handleCreateSigningLink = async () => {
  if (!contract.value) return

  try {
    const response = await contractSignApi.createLink(contract.value.id)
    ElMessage.success('签署链接创建成功')

    // 刷新签署信息
    await fetchSigningInfo(contract.value.id)

    // 显示签署链接
    await ElMessageBox.alert(`签署链接：${response.data.full_link}`, '签署链接创建成功', {
      confirmButtonText: '复制链接',
      callback: () => {
        navigator.clipboard.writeText(response.data.full_link)
        ElMessage.success('链接已复制到剪贴板')
      },
    })
  } catch (error) {
    ElMessage.error('创建签署链接失败')
  }
}

const handleCancelSigning = async () => {
  if (!contract.value) return

  try {
    const { value: reason } = await ElMessageBox.prompt('请输入取消原因', '取消签署', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValidator: (value) => {
        if (!value || value.trim().length === 0) {
          return '请输入取消原因'
        }
        return true
      },
    })

    await contractSignApi.cancel(contract.value.id, reason)
    ElMessage.success('签署已取消')

    // 刷新签署信息
    await fetchSigningInfo(contract.value.id)
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('取消签署失败')
    }
  }
}

const handleCreatePayment = async () => {
  if (!contract.value) return

  try {
    // 这里应该打开支付创建对话框
    // 暂时使用简单的提示
    ElMessage.info('支付创建功能开发中...')
  } catch (error) {
    ElMessage.error('创建支付失败')
  }
}

const handlePayment = (paymentRecord: PaymentInfoItem) => {
  // 跳转到支付页面
  router.push(`/contract-payment/${paymentRecord.id}`)
}

// 签名画布相关方法
const initSignatureCanvas = () => {
  if (!signatureCanvas.value) return

  const canvas = signatureCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.strokeStyle = '#000'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
}

const startDrawing = (e: MouseEvent) => {
  if (!signatureCanvas.value) return

  isDrawing.value = true
  const rect = signatureCanvas.value.getBoundingClientRect()
  lastX.value = e.clientX - rect.left
  lastY.value = e.clientY - rect.top
}

const draw = (e: MouseEvent) => {
  if (!isDrawing.value || !signatureCanvas.value) return

  const canvas = signatureCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const rect = canvas.getBoundingClientRect()
  const currentX = e.clientX - rect.left
  const currentY = e.clientY - rect.top

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
  if (!signatureCanvas.value) return

  const canvas = signatureCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
}

const confirmSignature = async () => {
  if (!contract.value) return

  try {
    signing.value = true

    const signatureData: { qianming_tupian?: string; qianming_wenben?: string } = {}

    if (signatureType.value === 'draw') {
      if (!signatureCanvas.value) {
        ElMessage.error('请先绘制签名')
        return
      }

      const canvas = signatureCanvas.value
      const dataURL = canvas.toDataURL('image/png')
      signatureData.qianming_tupian = dataURL
    } else {
      if (!textSignature.value.trim()) {
        ElMessage.error('请输入签名文字')
        return
      }

      signatureData.qianming_wenben = textSignature.value.trim()
    }

    await contractStore.signContract(contract.value.id, signatureData)

    signDialogVisible.value = false
    ElMessage.success('合同签署成功')

    // 刷新合同详情
    await fetchContractDetail()
  } catch (error) {
    ElMessage.error('签署合同失败')
  } finally {
    signing.value = false
  }
}

// 辅助方法
const getContractTypeLabel = (type: string) => {
  const option = contractTypeOptions.find((item) => item.value === type)
  return option?.label || type
}

const getContractStatusLabel = (status: string) => {
  const option = contractStatusOptions.find((item) => item.value === status)
  return option?.label || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    draft: 'info',
    pending_signature: 'warning',
    signed: 'success',
    active: 'success',
    completed: 'success',
    terminated: 'danger',
  }
  return typeMap[status] || 'info'
}

// 审核相关方法
const getAuditTimelineType = (status: string) => {
  const types: Record<string, string> = {
    shenhezhong: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    chexiao: 'info',
  }
  return types[status] || 'info'
}

const getAuditTimelineIcon = (status: string) => {
  const icons: Record<string, any> = {
    shenhezhong: Clock,
    tongguo: Check,
    jujue: Close,
    chexiao: Warning,
  }
  return icons[status] || Clock
}

const getAuditStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    shenhezhong: 'warning',
    tongguo: 'success',
    jujue: 'danger',
    chexiao: 'info',
  }
  return types[status] || 'info'
}

const getAuditStatusText = (status: string) => {
  const texts: Record<string, string> = {
    shenhezhong: '审核中',
    tongguo: '已通过',
    jujue: '已拒绝',
    chexiao: '已取消',
  }
  return texts[status] || status
}

const getAuditTypeText = (type: string) => {
  const texts: Record<string, string> = {
    hetong: '合同审核',
    baojia: '报价审核',
  }
  return texts[type] || type
}

// 签署相关方法
const getSigningStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    daiqianshu: 'warning',
    yiqianshu: 'success',
    guoqi: 'danger',
    yiquxiao: 'info',
  }
  return types[status] || 'info'
}

const getSigningStatusText = (status: string) => {
  const texts: Record<string, string> = {
    daiqianshu: '待签署',
    yiqianshu: '已签署',
    guoqi: '已过期',
    yiquxiao: '已取消',
  }
  return texts[status] || status
}

// 支付相关方法
const getPaymentMethodText = (method: string) => {
  const texts: Record<string, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    bank: '银行转账',
  }
  return texts[method] || method
}

const getPaymentStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    daizhi: 'warning',
    yizhifu: 'success',
    zhifushibai: 'danger',
    yituikuan: 'info',
  }
  return types[status] || 'info'
}

const getPaymentStatusText = (status: string) => {
  const texts: Record<string, string> = {
    daizhi: '待支付',
    yizhifu: '已支付',
    zhifushibai: '支付失败',
    yituikuan: '已退款',
  }
  return texts[status] || status
}

// 生命周期
onMounted(() => {
  fetchContractDetail()
})
</script>

<style scoped>
.contract-preview {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.contract-info {
  margin-bottom: 30px;
}

.amount {
  font-weight: bold;
  color: #e6a23c;
}

.contract-content {
  margin-bottom: 30px;
}

.contract-content h3 {
  margin-bottom: 15px;
  color: #303133;
}

.content-viewer {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  background-color: #fafafa;
  min-height: 300px;
  line-height: 1.6;
}

/* 审核流程样式 */
.audit-flow-section,
.signing-status-section,
.payment-status-section {
  margin-bottom: 30px;
}

.audit-flow-section h3,
.signing-status-section h3,
.payment-status-section h3 {
  margin-bottom: 15px;
  color: #303133;
}

.audit-card {
  margin-bottom: 8px;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.audit-title {
  font-weight: 600;
  color: #303133;
}

.audit-content p {
  margin: 4px 0;
  color: #606266;
}

/* 签署状态样式 */
.signing-info,
.no-signing-info {
  padding: 16px;
}

.signing-actions {
  margin-top: 16px;
  text-align: center;
}

.signing-actions .el-button {
  margin: 0 8px;
}

/* 支付状态样式 */
.payment-info,
.no-payment-info {
  padding: 16px;
}

.payment-actions {
  margin-top: 16px;
  text-align: center;
}

.signature-section h3 {
  margin-bottom: 15px;
  color: #303133;
}

.signature-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.signature-image img {
  max-width: 300px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.signature-dialog {
  padding: 20px 0;
}

.signature-canvas-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.signature-canvas-container canvas {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: crosshair;
}

.canvas-actions {
  display: flex;
  gap: 10px;
}

.text-signature-preview {
  margin-top: 20px;
  text-align: center;
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fafafa;
}

.signature-text {
  font-size: 24px;
  font-family: '楷体', 'KaiTi', serif;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
