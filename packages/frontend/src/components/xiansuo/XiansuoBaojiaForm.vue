<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'create' ? '创建报价' : '编辑报价'"
    width="900px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      v-loading="loading"
    >
      <!-- 基本信息 -->
      <el-card class="form-section" shadow="never">
        <template #header>
          <span class="section-title">基本信息</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="线索信息">
              <div class="xiansuo-info">
                <div class="company-name">{{ xiansuo?.gongsi_mingcheng }}</div>
                <div class="contact-info">{{ xiansuo?.lianxi_ren }} {{ xiansuo?.lianxi_dianhua }}</div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报价名称" prop="baojia_mingcheng">
              <el-input
                v-model="formData.baojia_mingcheng"
                placeholder="请输入报价名称"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="有效期" prop="youxiao_qi">
              <el-date-picker
                v-model="formData.youxiao_qi"
                type="date"
                placeholder="选择有效期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disabledDate"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认有效期">
              <div class="validity-info">
                <el-icon><Clock /></el-icon>
                <span>建议15天（{{ validityEndDate }}）</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input
            v-model="formData.beizhu"
            type="textarea"
            :rows="3"
            placeholder="请输入报价备注信息"
          />
        </el-form-item>
      </el-card>

      <!-- 服务项目 -->
      <el-card class="form-section" shadow="never">
        <template #header>
          <div class="section-header">
            <span class="section-title">服务项目</span>
            <el-button type="primary" size="small" @click="showProductSelector = true">
              <el-icon><Plus /></el-icon>
              添加服务
            </el-button>
          </div>
        </template>

        <div v-if="formData.xiangmu_list.length === 0" class="empty-state">
          <el-empty description="暂无服务项目，请点击上方按钮添加" />
        </div>

        <div v-else class="xiangmu-list">
          <div
            v-for="(item, index) in formData.xiangmu_list"
            :key="index"
            class="xiangmu-item"
          >
            <div class="xiangmu-header">
              <div class="xiangmu-title">
                <span class="name">{{ item.xiangmu_mingcheng }}</span>
                <el-tag v-if="item.danwei" size="small" type="success">
                  {{ item.danwei }}
                </el-tag>
              </div>
              <el-button
                type="danger"
                size="small"
                text
                @click="removeXiangmu(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>

            <el-row :gutter="20" class="xiangmu-content">
              <el-col :span="6">
                <el-form-item :label="`数量`" :prop="`xiangmu_list.${index}.shuliang`">
                  <el-input-number
                    v-model="item.shuliang"
                    :min="1"
                    :max="999"
                    controls-position="right"
                    class="number-input"
                    @change="calculateXiaoji(index)"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item :label="`单价`" :prop="`xiangmu_list.${index}.danjia`">
                  <el-input-number
                    v-model="item.danjia"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                    class="number-input"
                    @change="calculateXiaoji(index)"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="小计">
                  <div class="xiaoji-display">
                    ¥{{ calculateXiaoji(index).toFixed(2) }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="备注">
                  <el-input
                    v-model="item.beizhu"
                    placeholder="项目备注"
                    size="small"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 总计 -->
        <div v-if="formData.xiangmu_list.length > 0" class="total-section">
          <el-divider />
          <div class="total-row">
            <span class="total-label">报价总金额：</span>
            <span class="total-amount">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
        </div>
      </el-card>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ mode === 'create' ? '创建报价' : '更新报价' }}
        </el-button>
      </div>
    </template>

    <!-- 产品选择器 -->
    <ProductSelector
      v-model:visible="showProductSelector"
      @select="handleProductSelect"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { type FormInstance, type FormRules } from 'element-plus'
import { Clock, Plus, Delete } from '@element-plus/icons-vue'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import ProductSelector from './ProductSelector.vue'
import type {
  XiansuoBaojiaCreate,
  XiansuoBaojiaUpdate,
  XiansuoBaojia,
  XiansuoBaojiaXiangmuInput,
  ChanpinXiangmuOption,
  Xiansuo
} from '@/types/xiansuo'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit'
  xiansuo?: Xiansuo
  baojia?: XiansuoBaojia
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create'
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: [baojia: XiansuoBaojia]
}>()

// Store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const showProductSelector = ref(false)

interface QuoteItemForm extends XiansuoBaojiaXiangmuInput {
  shuliang: number
  danjia: number
  danwei?: string
  paixu?: number
}

interface QuoteFormState {
  xiansuo_id: string
  baojia_mingcheng: string
  youxiao_qi: string
  beizhu: string
  xiangmu_list: QuoteItemForm[]
}

// 表单数据
const formData = ref<QuoteFormState>({
  xiansuo_id: '',
  baojia_mingcheng: '',
  youxiao_qi: '',
  beizhu: '',
  xiangmu_list: []
})

// 表单验证规则
const formRules: FormRules = {
  baojia_mingcheng: [
    { required: true, message: '请输入报价名称', trigger: 'blur' }
  ],
  youxiao_qi: [
    { required: true, message: '请选择有效期', trigger: 'change' }
  ],
  xiangmu_list: [
    {
      type: 'array',
      min: 1,
      message: '请至少添加一个服务项目',
      trigger: 'change'
    }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const totalAmount = computed(() => {
  return formData.value.xiangmu_list.reduce((sum, item) =>
    sum + item.shuliang * item.danjia
  , 0)
})

const validityEndDate = computed(() => {
  const date = new Date()
  date.setDate(date.getDate() + 15)
  return date.toLocaleDateString('zh-CN')
})

// 方法
const disabledDate = (time: Date) => {
  // 不能选择今天之前的日期
  return time.getTime() < Date.now() - 8.64e7
}

const calculateXiaoji = (index: number) => {
  const item = formData.value.xiangmu_list[index]
  if (!item) return 0
  const value = item.shuliang * item.danjia
  return value
}

const removeXiangmu = (index: number) => {
  formData.value.xiangmu_list.splice(index, 1)
  formData.value.xiangmu_list.forEach((item, idx) => {
    item.paixu = idx
  })
}

const handleProductSelect = (products: ChanpinXiangmuOption[]) => {
  products.forEach(product => {
    if (formData.value.xiangmu_list.some(item => item.chanpin_xiangmu_id === product.id)) {
      return
    }

    const xiangmu: QuoteItemForm = {
      chanpin_xiangmu_id: product.id,
      xiangmu_mingcheng: product.xiangmu_mingcheng,
      shuliang: 1,
      danjia: product.yewu_baojia || 0,
      danwei: product.baojia_danwei,
      paixu: formData.value.xiangmu_list.length,
      beizhu: ''
    }
    formData.value.xiangmu_list.push(xiangmu)
  })
}

const resetForm = () => {
  // 设置默认有效期为15天后
  const defaultDate = new Date()
  defaultDate.setDate(defaultDate.getDate() + 15)

  formData.value = {
    xiansuo_id: props.xiansuo?.id || '',
    baojia_mingcheng: props.xiansuo ? `${props.xiansuo.gongsi_mingcheng}报价单` : '新报价单',
    youxiao_qi: defaultDate.toISOString().split('T')[0],
    beizhu: '',
    xiangmu_list: []
  }
}

const loadBaojiaData = () => {
  if (props.mode === 'edit' && props.baojia) {
    formData.value = {
      xiansuo_id: props.baojia.xiansuo_id,
      baojia_mingcheng: props.baojia.baojia_mingcheng,
      youxiao_qi: props.baojia.youxiao_qi.split('T')[0], // 转换为日期格式
      beizhu: props.baojia.beizhu || '',
      xiangmu_list: props.baojia.xiangmu_list.map(item => ({
        chanpin_xiangmu_id: item.chanpin_xiangmu_id,
        xiangmu_mingcheng: item.xiangmu_mingcheng,
        shuliang: item.shuliang,
        danjia: item.danjia,
        danwei: item.danwei,
        paixu: item.paixu,
        beizhu: item.beizhu || ''
      }))
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    let result: XiansuoBaojia
    const normalizedItems: XiansuoBaojiaXiangmuInput[] = formData.value.xiangmu_list.map((item, index) => ({
      chanpin_xiangmu_id: item.chanpin_xiangmu_id,
      xiangmu_mingcheng: item.xiangmu_mingcheng,
      shuliang: item.shuliang,
      danjia: item.danjia,
      danwei: item.danwei,
      paixu: item.paixu ?? index,
      beizhu: item.beizhu
    }))

    const youxiaoQiISO = new Date(formData.value.youxiao_qi + 'T00:00:00').toISOString()

    if (props.mode === 'create') {
      const createData: XiansuoBaojiaCreate = {
        xiansuo_id: formData.value.xiansuo_id,
        baojia_mingcheng: formData.value.baojia_mingcheng,
        youxiao_qi: youxiaoQiISO,
        beizhu: formData.value.beizhu,
        xiangmu_list: normalizedItems
      }
      result = await xiansuoStore.createBaojia(createData)
    } else {
      const updateData: XiansuoBaojiaUpdate = {
        baojia_mingcheng: formData.value.baojia_mingcheng,
        youxiao_qi: youxiaoQiISO,
        beizhu: formData.value.beizhu,
        xiangmu_list: normalizedItems
      }
      result = await xiansuoStore.updateBaojia(props.baojia!.id, updateData)
    }

    emit('success', result)
    handleClose()
  } catch (error) {
    console.error('提交报价失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  nextTick(() => {
    formRef.value?.resetFields()
    resetForm()
  })
}

// 监听器
watch(() => props.visible, (visible) => {
  if (visible) {
    if (props.mode === 'create') {
      resetForm()
    } else {
      loadBaojiaData()
    }
  }
})
</script>

<style scoped>
.form-section {
  margin-bottom: 20px;
}

.form-section :deep(.el-card__body) {
  padding: 20px;
}

.section-title {
  font-weight: 600;
  color: #303133;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.xiansuo-info .company-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.xiansuo-info .contact-info {
  color: #909399;
  font-size: 14px;
}

.validity-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409EFF;
}

.empty-state {
  padding: 40px 0;
}

.xiangmu-list {
  space-y: 16px;
}

.xiangmu-item {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.xiangmu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.xiangmu-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.xiangmu-title .name {
  font-weight: 600;
  color: #303133;
}

.xiangmu-content {
  margin-top: 16px;
}

.xiaoji-display {
  font-weight: 600;
  color: #E6A23C;
  font-size: 16px;
}

.total-section {
  margin-top: 20px;
}

.total-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  font-size: 18px;
}

.total-label {
  color: #303133;
  font-weight: 600;
}

.total-amount {
  color: #E6A23C;
  font-weight: 700;
  font-size: 20px;
}

.number-input {
  width: 140px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
