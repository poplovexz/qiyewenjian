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
          <el-descriptions-item label="报价编号">{{ quoteInfo.baojia_bianma }}</el-descriptions-item>
          <el-descriptions-item label="报价名称">{{ quoteInfo.baojia_mingcheng }}</el-descriptions-item>
          <el-descriptions-item label="客户名称">{{ quoteInfo.xiansuo?.kehu?.gongsi_mingcheng }}</el-descriptions-item>
          <el-descriptions-item label="报价金额">¥{{ quoteInfo.zongji_jine }}</el-descriptions-item>
          <el-descriptions-item label="报价状态">
            <el-tag :type="getQuoteStatusType(quoteInfo.baojia_zhuangtai)">
              {{ getQuoteStatusText(quoteInfo.baojia_zhuangtai) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="有效期">{{ formatDate(quoteInfo.youxiao_qi) }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 合同生成配置 -->
      <div class="contract-config">
        <h3>合同生成配置</h3>
        
        <!-- 合同类型选择 -->
        <el-form :model="generateForm" :rules="generateRules" ref="generateFormRef" label-width="120px">
          <el-form-item label="合同类型" prop="contractTypes">
            <el-checkbox-group v-model="generateForm.contractTypes">
              <el-checkbox label="daili_jizhang">代理记账合同</el-checkbox>
              <el-checkbox label="zengzhi_fuwu">增值服务合同</el-checkbox>
            </el-checkbox-group>
            <div class="form-tip">可以选择生成一种或两种类型的合同</div>
          </el-form-item>

          <!-- 代理记账合同配置 -->
          <div v-if="generateForm.contractTypes.includes('daili_jizhang')" class="contract-type-config">
            <h4>代理记账合同配置</h4>
            
            <el-form-item label="合同价格" prop="daliJizhangPrice">
              <el-input-number
                v-model="generateForm.daliJizhangPrice"
                :min="0"
                :precision="2"
                placeholder="请输入合同价格"
                style="width: 200px"
              />
              <span class="price-diff" v-if="getDaliJizhangPriceDiff() !== 0">
                (与报价差异: {{ getDaliJizhangPriceDiff() > 0 ? '+' : '' }}¥{{ getDaliJizhangPriceDiff() }})
              </span>
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
          <div v-if="generateForm.contractTypes.includes('zengzhi_fuwu')" class="contract-type-config">
            <h4>增值服务合同配置</h4>
            
            <el-form-item label="合同价格" prop="zengzhiFuwuPrice">
              <el-input-number
                v-model="generateForm.zengzhiFuwuPrice"
                :min="0"
                :precision="2"
                placeholder="请输入合同价格"
                style="width: 200px"
              />
              <span class="price-diff" v-if="getZengzhiFuwuPriceDiff() !== 0">
                (与报价差异: {{ getZengzhiFuwuPriceDiff() > 0 ? '+' : '' }}¥{{ getZengzhiFuwuPriceDiff() }})
              </span>
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
              <el-button 
                type="primary" 
                @click="handlePreview"
                :loading="previewLoading"
              >
                预览合同
              </el-button>
              <el-button 
                type="success" 
                @click="handleGenerate"
                :loading="generateLoading"
              >
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
            <div class="preview-content" v-html="previewContent.daili_jizhang"></div>
          </el-tab-pane>
          <el-tab-pane 
            v-if="generateForm.contractTypes.includes('zengzhi_fuwu')"
            label="增值服务合同"
            name="zengzhi_fuwu"
          >
            <div class="preview-content" v-html="previewContent.zengzhi_fuwu"></div>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Warning } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import { useAuditStore } from '@/stores/modules/audit'
import { contractApi } from '@/api/modules/contract'

const route = useRoute()
const router = useRouter()
const xiansuoStore = useXiansuoStore()
const contractStore = useContractManagementStore()
const auditStore = useAuditStore()

// 响应式数据
const quoteInfo = ref(null)
const contractParties = ref([])
const previewLoading = ref(false)
const generateLoading = ref(false)
const auditLoading = ref(false)
const previewDialogVisible = ref(false)
const auditDialogVisible = ref(false)
const activePreviewTab = ref('daili_jizhang')

// 表单数据
const generateForm = reactive({
  contractTypes: ['daili_jizhang'], // 默认选择代理记账
  daliJizhangPrice: 0,
  daliJizhangCount: 1,
  daliJizhangParty: '',
  daliJizhangReason: '',
  zengzhiFuwuPrice: 0,
  zengzhiFuwuCount: 1,
  zengzhiFuwuParty: '',
  zengzhiFuwuReason: ''
})

// 预览内容
const previewContent = reactive({
  daili_jizhang: '',
  zengzhi_fuwu: ''
})

// 审核信息
const auditInfo = reactive({
  reason: '',
  priceDiff: 0
})

// 表单验证规则
const generateRules = {
  contractTypes: [
    { required: true, message: '请选择至少一种合同类型', trigger: 'change' }
  ],
  daliJizhangPrice: [
    { required: true, message: '请输入代理记账合同价格', trigger: 'blur' }
  ],
  daliJizhangParty: [
    { required: true, message: '请选择乙方主体', trigger: 'change' }
  ],
  zengzhiFuwuPrice: [
    { required: true, message: '请输入增值服务合同价格', trigger: 'blur' }
  ],
  zengzhiFuwuParty: [
    { required: true, message: '请选择乙方主体', trigger: 'change' }
  ]
}

const generateFormRef = ref()

// 计算属性
const getDaliJizhangPriceDiff = () => {
  if (!quoteInfo.value) return 0
  return generateForm.daliJizhangPrice - quoteInfo.value.zongji_jine
}

const getZengzhiFuwuPriceDiff = () => {
  if (!quoteInfo.value) return 0
  return generateForm.zengzhiFuwuPrice - quoteInfo.value.zongji_jine
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
    
    // 初始化价格
    generateForm.daliJizhangPrice = quote.zongji_jine
    generateForm.zengzhiFuwuPrice = quote.zongji_jine
  } catch (error) {
    console.error('获取报价信息失败:', error)
    ElMessage.error('获取报价信息失败')
    handleBack()
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
  const types = {
    draft: '',
    sent: 'warning',
    accepted: 'success',
    rejected: 'danger',
    expired: 'info'
  }
  return types[status] || ''
}

const getQuoteStatusText = (status: string) => {
  const texts = {
    draft: '草稿',
    sent: '已发送',
    accepted: '已接受',
    rejected: '已拒绝',
    expired: '已过期'
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
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
    previewLoading.value = true
    
    // 预览代理记账合同
    if (generateForm.contractTypes.includes('daili_jizhang')) {
      const previewData = {
        hetong_moban_id: 'daili_jizhang_template_id', // 需要从模板列表获取
        kehu_id: quoteInfo.value.xiansuo.kehu.id,
        bianliang_zhis: {
          hetong_jine: generateForm.daliJizhangPrice,
          kehu_mingcheng: quoteInfo.value.xiansuo.kehu.gongsi_mingcheng,
          // 其他变量...
        }
      }
      
      const response = await contractApi.previewContract(previewData)
      previewContent.daili_jizhang = response.data.content
    }
    
    // 预览增值服务合同
    if (generateForm.contractTypes.includes('zengzhi_fuwu')) {
      const previewData = {
        hetong_moban_id: 'zengzhi_fuwu_template_id', // 需要从模板列表获取
        kehu_id: quoteInfo.value.xiansuo.kehu.id,
        bianliang_zhis: {
          hetong_jine: generateForm.zengzhiFuwuPrice,
          kehu_mingcheng: quoteInfo.value.xiansuo.kehu.gongsi_mingcheng,
          // 其他变量...
        }
      }
      
      const response = await contractApi.previewContract(previewData)
      previewContent.zengzhi_fuwu = response.data.content
    }
    
    previewDialogVisible.value = true
    activePreviewTab.value = generateForm.contractTypes[0]
    
  } catch (error) {
    console.error('预览合同失败:', error)
    if (error !== false) { // 不是表单验证错误
      ElMessage.error('预览合同失败')
    }
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
    if (error !== false) { // 不是表单验证错误
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
    
    // 提交审核申请
    const auditData = {
      audit_type: 'hetong_jine_xiuzheng',
      related_id: quoteInfo.value.id,
      trigger_data: {
        original_amount: quoteInfo.value.zongji_jine,
        new_amount: generateForm.daliJizhangPrice || generateForm.zengzhiFuwuPrice,
        change_reason: generateForm.daliJizhangReason || generateForm.zengzhiFuwuReason,
        contract_types: generateForm.contractTypes
      }
    }
    
    await auditStore.submitAudit(auditData)
    
    ElMessage.success('审核申请已提交，请等待审核结果')
    auditDialogVisible.value = false
    handleBack()
    
  } catch (error) {
    console.error('提交审核失败:', error)
    ElMessage.error('提交审核失败')
  } finally {
    auditLoading.value = false
  }
}

const generateContracts = async () => {
  generateLoading.value = true

  try {
    // 准备合同生成数据
    const generateData = {
      baojia_id: quoteInfo.value.id,
      contract_types: generateForm.contractTypes,
      daili_jizhang_config: generateForm.contractTypes.includes('daili_jizhang') ? {
        price: generateForm.daliJizhangPrice,
        count: generateForm.daliJizhangCount,
        party_id: generateForm.daliJizhangParty,
        price_change_reason: generateForm.daliJizhangReason
      } : null,
      zengzhi_fuwu_config: generateForm.contractTypes.includes('zengzhi_fuwu') ? {
        price: generateForm.zengzhiFuwuPrice,
        count: generateForm.zengzhiFuwuCount,
        party_id: generateForm.zengzhiFuwuParty,
        price_change_reason: generateForm.zengzhiFuwuReason
      } : null
    }

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

  } catch (error) {
    console.error('生成合同失败:', error)
    ElMessage.error('生成合同失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generateLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchQuoteInfo()
  fetchContractParties()
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

.price-diff {
  margin-left: 10px;
  font-size: 12px;
  color: #e6a23c;
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
