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

      <el-form-item label="支付配置" prop="zhifu_peizhi_id">
        <el-select
          v-model="form.zhifu_peizhi_id"
          placeholder="请选择支付配置"
          style="width: 100%"
          filterable
          @change="handlePaymentConfigChange"
        >
          <el-option
            v-for="config in paymentConfigs"
            :key="config.id"
            :label="`${config.peizhi_mingcheng} (${config.peizhi_leixing === 'weixin' ? '微信支付' : '支付宝'})`"
            :value="config.id"
          >
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ config.peizhi_mingcheng }}</span>
              <el-tag :type="config.peizhi_leixing === 'weixin' ? 'success' : 'primary'" size="small">
                {{ config.peizhi_leixing === 'weixin' ? '微信支付' : '支付宝' }}
              </el-tag>
            </div>
          </el-option>
        </el-select>
        <div v-if="paymentConfigs.length === 0" class="upload-tip" style="color: #f56c6c;">
          ⚠️ 暂无可用的支付配置，请先在
          <router-link to="/finance/payment-configs" style="color: #409eff;">支付配置管理</router-link>
          中创建微信支付或支付宝配置
        </div>
        <div v-else class="upload-tip">选择已配置的商户支付方式</div>
      </el-form-item>

      <el-form-item label="支付名称" prop="zhifu_mingcheng">
        <el-input
          v-model="form.zhifu_mingcheng"
          placeholder="请输入支付方式名称"
        />
        <div class="upload-tip">用于在合同中显示的支付方式名称</div>
      </el-form-item>

      <el-form-item label="是否默认">
        <el-switch
          v-model="form.shi_moren"
          active-value="Y"
          inactive-value="N"
          active-text="是"
          inactive-text="否"
        />
        <div class="upload-tip">设为默认后，新建合同时将自动选择此支付方式</div>
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group v-model="form.zhifu_zhuangtai">
          <el-radio value="active">启用</el-radio>
          <el-radio value="inactive">停用</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="排序">
        <el-input
          v-model="form.paixu"
          placeholder="请输入排序值（数字）"
        />
        <div class="upload-tip">数值越小越靠前，默认为0</div>
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
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useContractManagementStore } from '@/stores/modules/contractManagement'
import type { PaymentMethodCreate, PaymentMethodUpdate, ContractParty } from '@/api/modules/contract'
import { getZhifuPeizhiList, type ZhifuPeizhi } from '@/api/modules/payment-config'

const route = useRoute()
const router = useRouter()
const contractStore = useContractManagementStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const contractParties = ref<ContractParty[]>([])
const paymentConfigs = ref<ZhifuPeizhi[]>([])

// 是否编辑模式
const isEdit = computed(() => Boolean(route.params.id))

// 表单数据
const form = reactive<PaymentMethodCreate & { id?: string }>({
  yifang_zhuti_id: '',
  zhifu_peizhi_id: '',
  zhifu_mingcheng: '',
  shi_moren: 'N',
  zhifu_zhuangtai: 'active',
  paixu: '0',
  beizhu: ''
})

// 表单验证规则
const rules: FormRules = {
  yifang_zhuti_id: [
    { required: true, message: '请选择乙方主体', trigger: 'change' }
  ],
  zhifu_peizhi_id: [
    { required: true, message: '请选择支付配置', trigger: 'change' }
  ],
  zhifu_mingcheng: [
    { required: true, message: '请输入支付方式名称', trigger: 'blur' },
    { min: 2, max: 100, message: '支付方式名称长度在 2 到 100 个字符', trigger: 'blur' }
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

// 加载支付配置列表
const loadPaymentConfigs = async () => {
  try {
    const response = await getZhifuPeizhiList({ page: 1, page_size: 100, zhuangtai: 'qiyong' })
    paymentConfigs.value = response.items

    if (response.items.length === 0) {
      ElMessage.warning({
        message: '暂无可用的支付配置，请先在"支付配置管理"中创建微信支付或支付宝配置',
        duration: 5000
      })
    }
  } catch (error) {
    console.error('加载支付配置列表失败:', error)
    ElMessage.error('加载支付配置列表失败')
  }
}

// 支付配置变更时自动填充名称
const handlePaymentConfigChange = (configId: string) => {
  const config = paymentConfigs.value.find(c => c.id === configId)
  if (config && !form.zhifu_mingcheng) {
    form.zhifu_mingcheng = config.peizhi_mingcheng
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

// 初始化
onMounted(async () => {
  await Promise.all([
    loadContractParties(),
    loadPaymentConfigs(),
    loadPaymentMethodDetail()
  ])
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

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
