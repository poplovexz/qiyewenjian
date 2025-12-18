<template>
  <div class="contract-generate">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合同生成</span>
          <el-button @click="handleBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>

      <!-- 报价信息展示 -->
      <div class="quote-info" v-if="quoteInfo">
        <h3>报价信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报价编号">{{
            quoteInfo.baojia_bianma
          }}</el-descriptions-item>
          <el-descriptions-item label="报价名称">{{
            quoteInfo.baojia_mingcheng
          }}</el-descriptions-item>
          <el-descriptions-item label="客户名称">{{
            quoteInfo.xiansuo_info?.gongsi_mingcheng
          }}</el-descriptions-item>
          <el-descriptions-item label="报价金额">¥{{ quoteInfo.zongji_jine }}</el-descriptions-item>
          <el-descriptions-item label="报价状态">
            <el-tag :type="getQuoteStatusType(quoteInfo.baojia_zhuangtai)">
              {{ getQuoteStatusText(quoteInfo.baojia_zhuangtai) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="有效期">{{
            formatDate(quoteInfo.youxiao_qi)
          }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 合同生成配置 -->
      <div class="contract-config">
        <h3>合同生成配置</h3>

        <!-- 合同类型选择 -->
        <el-form
          :model="generateForm"
          :rules="generateRules"
          ref="generateFormRef"
          label-width="120px"
        >
          <el-form-item label="合同类型" prop="contractTypes">
            <el-checkbox-group v-model="generateForm.contractTypes">
              <el-checkbox label="daili_jizhang">代理记账合同</el-checkbox>
              <el-checkbox label="zengzhi_fuwu">增值服务合同</el-checkbox>
            </el-checkbox-group>
            <div class="form-tip">可以选择生成一种或两种类型的合同</div>
          </el-form-item>

          <!-- 代理记账合同配置 -->
          <div
            v-if="generateForm.contractTypes.includes('daili_jizhang')"
            class="contract-type-config"
          >
            <h4>代理记账合同配置</h4>

            <el-form-item label="合同模板" prop="daliJizhangTemplate">
              <el-select
                v-model="generateForm.daliJizhangTemplate"
                placeholder="请选择代理记账合同模板"
                style="width: 400px"
                filterable
              >
                <el-option
                  v-for="template in getDaliJizhangTemplates()"
                  :key="template.id"
                  :label="template.moban_mingcheng"
                  :value="template.id"
                />
              </el-select>
              <div class="form-tip">选择用于生成代理记账合同的模板</div>
            </el-form-item>

            <el-form-item label="合同价格" prop="daliJizhangPrice">
              <el-input-number
                v-model="generateForm.daliJizhangPrice"
                :min="0"
                :precision="2"
                placeholder="请输入合同价格"
                style="width: 200px"
              />
              <div v-if="getDaliJizhangPriceDiff() !== 0" class="price-info">
                <span class="price-diff" v-if="getDaliJizhangPriceDiff() > 0">
                  (价格上调: +¥{{ getDaliJizhangPriceDiff().toFixed(2) }})
                </span>
                <span class="price-discount" v-else>
                  (优惠价格: -¥{{ Math.abs(getDaliJizhangPriceDiff()).toFixed(2) }})
                </span>
              </div>
              <div v-if="getDaliJizhangOriginalPrice() > 0" class="original-price">
                原报价: ¥{{ getDaliJizhangOriginalPrice().toFixed(2) }}
              </div>
            </el-form-item>

            <el-form-item label="合同数量" prop="daliJizhangCount">
              <el-input-number
                v-model="generateForm.daliJizhangCount"
                :min="1"
                :max="10"
                placeholder="请输入合同数量"
                style="width: 200px"
              />
            </el-form-item>

            <el-form-item label="乙方主体" prop="daliJizhangParty">
              <el-select
                v-model="generateForm.daliJizhangParty"
                placeholder="请选择乙方主体"
                style="width: 300px"
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

            <el-form-item label="价格调整原因" v-if="getDaliJizhangPriceDiff() !== 0">
              <el-input
                v-model="generateForm.daliJizhangReason"
                type="textarea"
                :rows="3"
                placeholder="请说明价格调整的原因"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
          </div>

          <!-- 增值服务合同配置 -->
          <div
            v-if="generateForm.contractTypes.includes('zengzhi_fuwu')"
            class="contract-type-config"
          >
            <h4>增值服务合同配置</h4>

            <el-form-item label="合同模板" prop="zengzhiFuwuTemplate">
              <el-select
                v-model="generateForm.zengzhiFuwuTemplate"
                placeholder="请选择增值服务合同模板"
                style="width: 400px"
                filterable
              >
                <el-option
                  v-for="template in getZengzhiFuwuTemplates()"
                  :key="template.id"
                  :label="template.moban_mingcheng"
                  :value="template.id"
                />
              </el-select>
              <div class="form-tip">选择用于生成增值服务合同的模板</div>
            </el-form-item>

            <el-form-item label="合同价格" prop="zengzhiFuwuPrice">
              <el-input-number
                v-model="generateForm.zengzhiFuwuPrice"
                :min="0"
                :precision="2"
                placeholder="请输入合同价格"
                style="width: 200px"
              />
              <div v-if="getZengzhiFuwuPriceDiff() !== 0" class="price-info">
                <span class="price-diff" v-if="getZengzhiFuwuPriceDiff() > 0">
                  (价格上调: +¥{{ getZengzhiFuwuPriceDiff().toFixed(2) }})
                </span>
                <span class="price-discount" v-else>
                  (优惠价格: -¥{{ Math.abs(getZengzhiFuwuPriceDiff()).toFixed(2) }})
                </span>
              </div>
              <div v-if="getZengzhiFuwuOriginalPrice() > 0" class="original-price">
                原报价: ¥{{ getZengzhiFuwuOriginalPrice().toFixed(2) }}
              </div>
            </el-form-item>

            <el-form-item label="合同数量" prop="zengzhiFuwuCount">
              <el-input-number
                v-model="generateForm.zengzhiFuwuCount"
                :min="1"
                :max="10"
                placeholder="请输入合同数量"
                style="width: 200px"
              />
            </el-form-item>

            <el-form-item label="乙方主体" prop="zengzhiFuwuParty">
              <el-select
                v-model="generateForm.zengzhiFuwuParty"
                placeholder="请选择乙方主体"
                style="width: 300px"
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

            <el-form-item label="价格调整原因" v-if="getZengzhiFuwuPriceDiff() !== 0">
              <el-input
                v-model="generateForm.zengzhiFuwuReason"
                type="textarea"
                :rows="3"
                placeholder="请说明价格调整的原因"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
          </div>

          <!-- 操作按钮 -->
          <el-form-item>
            <div class="form-actions">
              <el-button @click="handleBack">取消</el-button>
              <el-button type="primary" @click="handlePreview" :loading="previewLoading">
                预览合同
              </el-button>
              <el-button type="success" @click="handleGenerate" :loading="generateLoading">
                生成合同
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="合同预览"
      width="80%"
      :close-on-click-modal="false"
    >
      <div class="contract-preview">
        <el-tabs v-model="activePreviewTab" type="border-card">
          <el-tab-pane
            v-if="generateForm.contractTypes.includes('daili_jizhang')"
            label="代理记账合同"
            name="daili_jizhang"
          >
            <div
              class="preview-content"
              v-html="sanitizeContractHtml(previewContent.daili_jizhang)"
            ></div>
          </el-tab-pane>
          <el-tab-pane
            v-if="generateForm.contractTypes.includes('zengzhi_fuwu')"
            label="增值服务合同"
            name="zengzhi_fuwu"
          >
            <div
              class="preview-content"
              v-html="sanitizeContractHtml(previewContent.zengzhi_fuwu)"
            ></div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="previewDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleGenerate" :loading="generateLoading">
            确认生成
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 审核提示对话框 -->
    <el-dialog
      v-model="auditDialogVisible"
      title="需要审核"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="audit-info">
        <el-icon class="audit-icon"><Warning /></el-icon>
        <p>由于价格调整超过了系统设定的阈值，需要提交审核。</p>
        <div class="audit-details">
          <p><strong>审核原因：</strong>{{ auditInfo.reason }}</p>
          <p><strong>价格差异：</strong>¥{{ auditInfo.priceDiff }}</p>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="auditDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitAudit" :loading="auditLoading">
            提交审核
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Warning } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { contractApi } from '@/api/modules/contract'
import type { XiansuoBaojiaDetail } from '@/types/xiansuo'
import type { ContractParty } from '@/api/modules/contract'
import { sanitizeContractHtml } from '@/utils/sanitize'

const route = useRoute()
const router = useRouter()
const xiansuoStore = useXiansuoStore()
const contractStore = useContractManagementStore()

// 响应式数据
const quoteInfo = ref<XiansuoBaojiaDetail | null>(null)
const contractParties = ref<ContractParty[]>([])
const contractTemplates = ref<any[]>([])
const previewLoading = ref(false)
const generateLoading = ref(false)
const auditLoading = ref(false)
const previewDialogVisible = ref(false)
const auditDialogVisible = ref(false)
const activePreviewTab = ref('daili_jizhang')

// 表单数据
const generateForm = reactive({
  contractTypes: ['daili_jizhang'], // 默认选择代理记账
  daliJizhangTemplate: '',
  daliJizhangPrice: 0,
  daliJizhangCount: 1,
  daliJizhangParty: '',
  daliJizhangReason: '',
  zengzhiFuwuTemplate: '',
  zengzhiFuwuPrice: 0,
  zengzhiFuwuCount: 1,
  zengzhiFuwuParty: '',
  zengzhiFuwuReason: '',
})

// 预览内容
const previewContent = reactive({
  daili_jizhang: '',
  zengzhi_fuwu: '',
})

// 审核信息
const auditInfo = reactive({
  reason: '',
  priceDiff: 0,
})

// 表单验证规则
const generateRules = {
  contractTypes: [{ required: true, message: '请选择至少一种合同类型', trigger: 'change' }],
  daliJizhangTemplate: [{ required: true, message: '请选择代理记账合同模板', trigger: 'change' }],
  daliJizhangPrice: [{ required: true, message: '请输入代理记账合同价格', trigger: 'blur' }],
  daliJizhangParty: [{ required: true, message: '请选择乙方主体', trigger: 'change' }],
  zengzhiFuwuTemplate: [{ required: true, message: '请选择增值服务合同模板', trigger: 'change' }],
  zengzhiFuwuPrice: [{ required: true, message: '请输入增值服务合同价格', trigger: 'blur' }],
  zengzhiFuwuParty: [{ required: true, message: '请选择乙方主体', trigger: 'change' }],
}

const generateFormRef = ref()

// 计算属性
const getDaliJizhangOriginalPrice = () => {
  if (!quoteInfo.value) return 0
  // 计算代理记账服务的原始报价金额
  const daliJizhangItems = quoteInfo.value.xiangmu_list.filter(
    (item: any) =>
      item.xiangmu_mingcheng.includes('代理记账') ||
      item.xiangmu_mingcheng.includes('记账') ||
      item.xiangmu_mingcheng.includes('纳税人')
  )
  return daliJizhangItems.reduce((sum: number, item: any) => sum + parseFloat(item.xiaoji), 0)
}

const getZengzhiFuwuOriginalPrice = () => {
  if (!quoteInfo.value) return 0
  // 计算增值服务的原始报价金额
  const zengzhiFuwuItems = quoteInfo.value.xiangmu_list.filter(
    (item: any) =>
      !item.xiangmu_mingcheng.includes('代理记账') &&
      !item.xiangmu_mingcheng.includes('记账') &&
      !item.xiangmu_mingcheng.includes('纳税人')
  )
  return zengzhiFuwuItems.reduce((sum: number, item: any) => sum + parseFloat(item.xiaoji), 0)
}

const getDaliJizhangPriceDiff = () => {
  const originalPrice = getDaliJizhangOriginalPrice()
  if (originalPrice === 0) return 0
  return generateForm.daliJizhangPrice - originalPrice
}

const getZengzhiFuwuPriceDiff = () => {
  const originalPrice = getZengzhiFuwuOriginalPrice()
  if (originalPrice === 0) return 0
  return generateForm.zengzhiFuwuPrice - originalPrice
}

// 方法
const fetchQuoteInfo = async () => {
  const baojiaId = route.query.baojia_id as string
  if (!baojiaId) {
    ElMessage.error('缺少报价ID参数')
    handleBack()
    return
  }

  try {
    const quote = await xiansuoStore.getBaojiaDetailWithXiansuo(baojiaId)
    quoteInfo.value = quote

    // 分析报价中的服务类型并自动分割合同
    analyzeQuoteServices(quote)
  } catch (error) {
    console.error('获取报价信息失败:', error)
    ElMessage.error('获取报价信息失败')
    handleBack()
  }
}

const fetchContractTemplates = async () => {
  try {
    const response = await contractApi.getTemplates()
    contractTemplates.value = response.data || []

    // 自动选择默认模板
    autoSelectDefaultTemplates()
  } catch (error) {
    console.error('获取合同模板失败:', error)
    ElMessage.error('获取合同模板失败')
  }
}

// 自动选择默认模板
const autoSelectDefaultTemplates = () => {
  // 如果包含代理记账合同类型且未选择模板，自动选择第一个代理记账模板
  if (generateForm.contractTypes.includes('daili_jizhang') && !generateForm.daliJizhangTemplate) {
    const daliJizhangTemplates = getDaliJizhangTemplates()
    if (daliJizhangTemplates.length > 0) {
      generateForm.daliJizhangTemplate = daliJizhangTemplates[0].id
    }
  }

  // 如果包含增值服务合同类型且未选择模板，自动选择第一个增值服务模板
  if (generateForm.contractTypes.includes('zengzhi_fuwu') && !generateForm.zengzhiFuwuTemplate) {
    const zengzhiFuwuTemplates = getZengzhiFuwuTemplates()
    if (zengzhiFuwuTemplates.length > 0) {
      generateForm.zengzhiFuwuTemplate = zengzhiFuwuTemplates[0].id
    }
  }
}

// 获取代理记账模板列表
const getDaliJizhangTemplates = () => {
  return contractTemplates.value.filter((template) => template.hetong_leixing === 'daili_jizhang')
}

// 获取增值服务模板列表
const getZengzhiFuwuTemplates = () => {
  return contractTemplates.value.filter((template) => template.hetong_leixing === 'zengzhi_fuwu')
}

const analyzeQuoteServices = (quote: XiansuoBaojiaDetail) => {
  // 分析报价项目，按服务类型分类
  const daliJizhangItems: any[] = []
  const zengzhiFuwuItems: any[] = []

  quote.xiangmu_list.forEach((item: any) => {
    // 根据产品项目的类型或名称判断服务类型
    if (
      item.xiangmu_mingcheng.includes('代理记账') ||
      item.xiangmu_mingcheng.includes('记账') ||
      item.xiangmu_mingcheng.includes('纳税人')
    ) {
      daliJizhangItems.push(item)
    } else {
      zengzhiFuwuItems.push(item)
    }
  })

  // 计算各类服务的价格
  const daliJizhangTotal = daliJizhangItems.reduce(
    (sum: number, item: any) => sum + parseFloat(item.xiaoji),
    0
  )
  const zengzhiFuwuTotal = zengzhiFuwuItems.reduce(
    (sum: number, item: any) => sum + parseFloat(item.xiaoji),
    0
  )

  // 自动选择需要生成的合同类型
  generateForm.contractTypes = []
  if (daliJizhangItems.length > 0) {
    generateForm.contractTypes.push('daili_jizhang')
    generateForm.daliJizhangPrice = daliJizhangTotal
  }
  if (zengzhiFuwuItems.length > 0) {
    generateForm.contractTypes.push('zengzhi_fuwu')
    generateForm.zengzhiFuwuPrice = zengzhiFuwuTotal
  }

  // 如果没有明确分类，默认为代理记账
  if (generateForm.contractTypes.length === 0) {
    generateForm.contractTypes = ['daili_jizhang']
    generateForm.daliJizhangPrice = quote.zongji_jine
  }
}

const fetchContractParties = async () => {
  try {
    const response = await contractStore.fetchParties()
    contractParties.value = response.items
  } catch (error) {
    console.error('获取乙方主体列表失败:', error)
    ElMessage.error('获取乙方主体列表失败')
  }
}

const getQuoteStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: '',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
    expired: 'info',
  }
  return types[status] || ''
}

const getQuoteStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    sent: '已发送',
    accepted: '已接受',
    rejected: '已拒绝',
    expired: '已过期',
  }
  return texts[status] || '未知'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

const handleBack = () => {
  router.back()
}

const handlePreview = async () => {
  // 检查报价信息是否存在
  if (!quoteInfo.value) {
    ElMessage.error('报价信息不存在，无法预览合同')
    return
  }

  // 表单验证
  const formRef = generateFormRef.value
  if (!formRef) return

  try {
    await formRef.validate()
  } catch (error) {
    ElMessage.error('请完善表单信息')
    return
  }

  previewLoading.value = true

  try {
    // 代理记账合同预览
    if (generateForm.contractTypes.includes('daili_jizhang')) {
      if (!generateForm.daliJizhangTemplate) {
        throw new Error('请选择代理记账合同模板')
      }

      // 验证必要的客户信息
      // 优先使用kehu_id，如果没有则使用线索ID（但会在后端报错）
      const kehuId = quoteInfo.value?.xiansuo_info?.kehu_id
      if (!kehuId) {
        throw new Error('该线索尚未关联客户，无法预览合同。请先完善客户信息。')
      }

      const previewData = {
        hetong_moban_id: generateForm.daliJizhangTemplate,
        kehu_id: kehuId,
        bianliang_zhis: {
          hetong_jine: generateForm.daliJizhangPrice,
          kehu_mingcheng: quoteInfo.value?.xiansuo_info?.gongsi_mingcheng || '测试公司',
        },
      }

      const response = await contractApi.previewContract(previewData)

      // 处理响应数据结构
      const content = response?.data?.content || response?.content || ''
      previewContent.daili_jizhang = content
    }

    // 增值服务合同预览
    if (generateForm.contractTypes.includes('zengzhi_fuwu')) {
      if (!generateForm.zengzhiFuwuTemplate) {
        throw new Error('请选择增值服务合同模板')
      }

      // 验证必要的客户信息
      const kehuId = quoteInfo.value?.xiansuo_info?.kehu_id
      if (!kehuId) {
        throw new Error('该线索尚未关联客户，无法预览合同。请先完善客户信息。')
      }

      const previewData = {
        hetong_moban_id: generateForm.zengzhiFuwuTemplate,
        kehu_id: kehuId,
        bianliang_zhis: {
          hetong_jine: generateForm.zengzhiFuwuPrice,
          kehu_mingcheng: quoteInfo.value?.xiansuo_info?.gongsi_mingcheng || '测试公司',
        },
      }

      const response = await contractApi.previewContract(previewData)

      // 处理响应数据结构
      const content = response?.data?.content || response?.content || ''
      previewContent.zengzhi_fuwu = content
    }

    previewDialogVisible.value = true
  } catch (error: any) {
    console.error('预览合同失败:', error)
    ElMessage.error(
      '预览合同失败: ' + (error?.response?.data?.detail || error?.message || '未知错误')
    )
  } finally {
    previewLoading.value = false
  }
}

const handleGenerate = async () => {
  if (!generateFormRef.value) return

  try {
    await generateFormRef.value.validate()

    // 检查是否需要审核
    const needsAudit = checkIfNeedsAudit()
    if (needsAudit) {
      showAuditDialog()
      return
    }

    // 直接生成合同
    await generateContracts()
  } catch (error) {
    console.error('生成合同失败:', error)
    if (error !== false) {
      // 不是表单验证错误
      ElMessage.error('生成合同失败')
    }
  }
}

const checkIfNeedsAudit = () => {
  // 检查价格差异是否超过阈值
  const daliJizhangDiff = Math.abs(getDaliJizhangPriceDiff())
  const zengzhiFuwuDiff = Math.abs(getZengzhiFuwuPriceDiff())

  const threshold = 1000 // 1000元阈值，可以从配置获取

  if (daliJizhangDiff > threshold || zengzhiFuwuDiff > threshold) {
    auditInfo.reason = '价格调整超过系统阈值'
    auditInfo.priceDiff = Math.max(daliJizhangDiff, zengzhiFuwuDiff)
    return true
  }

  return false
}

const showAuditDialog = () => {
  auditDialogVisible.value = true
}

const handleSubmitAudit = async () => {
  try {
    auditLoading.value = true

    if (!quoteInfo.value) {
      ElMessage.error('报价信息不存在')
      return
    }

    // 关闭审核对话框
    auditDialogVisible.value = false

    // 直接调用合同生成API，后端会自动触发审核流程
    await generateContracts()
  } catch (error: any) {
    console.error('提交审核失败:', error)
    const errorMsg = error?.response?.data?.detail || error?.message || '提交审核失败'
    ElMessage.error(String(errorMsg))
  } finally {
    auditLoading.value = false
  }
}

const generateContracts = async () => {
  // 检查报价信息是否存在
  if (!quoteInfo.value) {
    ElMessage.error('报价信息不存在，无法生成合同')
    return
  }

  generateLoading.value = true

  try {
    // 准备合同生成数据
    const generateData = {
      baojia_id: quoteInfo.value.id,
      contract_types: generateForm.contractTypes,
      daili_jizhang_config: generateForm.contractTypes.includes('daili_jizhang')
        ? {
            template_id: generateForm.daliJizhangTemplate,
            price: generateForm.daliJizhangPrice,
            count: generateForm.daliJizhangCount,
            party_id: generateForm.daliJizhangParty,
            price_change_reason: generateForm.daliJizhangReason,
          }
        : null,
      zengzhi_fuwu_config: generateForm.contractTypes.includes('zengzhi_fuwu')
        ? {
            template_id: generateForm.zengzhiFuwuTemplate,
            price: generateForm.zengzhiFuwuPrice,
            count: generateForm.zengzhiFuwuCount,
            party_id: generateForm.zengzhiFuwuParty,
            price_change_reason: generateForm.zengzhiFuwuReason,
          }
        : null,
    }

    // 调试：打印发送的数据

    // 调用新的合同生成API
    const response = await contractApi.generateContracts(generateData)

    if (response.data.audit_workflows && response.data.audit_workflows.length > 0) {
      // 有合同需要审核
      ElMessage.warning(response.message)
      router.push('/audit/tasks') // 跳转到审核任务页面
    } else {
      // 合同生成成功
      ElMessage.success(response.message)
      router.push('/contracts') // 跳转到合同列表
    }
  } catch (error: any) {
    console.error('生成合同失败:', error)
    ElMessage.error(
      '生成合同失败: ' + (error?.response?.data?.detail || error?.message || '未知错误')
    )
  } finally {
    generateLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchQuoteInfo()
  fetchContractParties()
  fetchContractTemplates()
})
</script>

<style scoped>
.contract-generate {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quote-info {
  margin-bottom: 30px;
}

.quote-info h3 {
  margin-bottom: 15px;
  color: #303133;
}

.contract-config h3 {
  margin-bottom: 20px;
  color: #303133;
}

.contract-type-config {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.contract-type-config h4 {
  margin-bottom: 15px;
  color: #606266;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.price-info {
  margin-top: 5px;
}

.price-diff {
  font-size: 12px;
  color: #e6a23c;
  font-weight: 500;
}

.price-discount {
  font-size: 12px;
  color: #67c23a;
  font-weight: 500;
}

.original-price {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.contract-preview {
  max-height: 600px;
  overflow-y: auto;
}

.preview-content {
  padding: 20px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  line-height: 1.6;
}

.audit-info {
  text-align: center;
  padding: 20px;
}

.audit-icon {
  font-size: 48px;
  color: #e6a23c;
  margin-bottom: 15px;
}

.audit-details {
  margin-top: 20px;
  text-align: left;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.audit-details p {
  margin: 5px 0;
}
</style>
