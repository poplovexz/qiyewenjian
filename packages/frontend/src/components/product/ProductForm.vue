<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    :title="dialogTitle"
    width="700px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      v-loading="submitting"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="项目名称" prop="xiangmu_mingcheng">
            <el-input
              v-model="formData.xiangmu_mingcheng"
              placeholder="请输入项目名称"
              :disabled="mode === 'view'"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="项目编码" prop="xiangmu_bianma">
            <el-input
              v-model="formData.xiangmu_bianma"
              placeholder="系统自动生成"
              disabled
              maxlength="50"
            >
              <template #append>
                <el-tag type="info" size="small">自动生成</el-tag>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="产品分类" prop="fenlei_id">
        <el-select
          v-model="formData.fenlei_id"
          placeholder="请选择产品分类"
          :disabled="mode === 'view'"
          style="width: 100%"
          filterable
        >
          <el-option
            v-for="option in categoryOptions"
            :key="option.id"
            :label="option.fenlei_mingcheng"
            :value="option.id"
          >
            <div class="option-content">
              <span class="option-label">{{ option.fenlei_mingcheng }}</span>
              <el-tag
                :type="option.chanpin_leixing === 'zengzhi' ? 'primary' : 'success'"
                size="small"
                class="option-tag"
              >
                {{ getProductTypeLabel(option.chanpin_leixing) }}
              </el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="业务报价" prop="yewu_baojia">
            <el-input-number
              v-model="formData.yewu_baojia"
              :min="0"
              :precision="2"
              :disabled="mode === 'view'"
              style="width: 100%"
              placeholder="请输入业务报价"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="报价单位" prop="baojia_danwei">
            <el-select
              v-model="formData.baojia_danwei"
              placeholder="请选择报价单位"
              :disabled="mode === 'view'"
              style="width: 100%"
            >
              <el-option
                v-for="option in priceUnitOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="办事天数" prop="banshi_tianshu">
            <el-input-number
              v-model="formData.banshi_tianshu"
              :min="1"
              :max="365"
              :disabled="mode === 'view'"
              style="width: 100%"
              placeholder="请输入办事天数"
            />
            <div class="form-tip">预计完成该项目所需的工作日天数</div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="排序号" prop="paixu">
            <el-input-number
              v-model="formData.paixu"
              :min="0"
              :max="9999"
              :disabled="mode === 'view'"
              style="width: 100%"
            />
            <div class="form-tip">数字越小排序越靠前</div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="状态" prop="zhuangtai">
        <el-radio-group
          v-model="formData.zhuangtai"
          :disabled="mode === 'view'"
        >
          <el-radio
            v-for="option in productStatusOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="项目备注" prop="xiangmu_beizhu">
        <el-input
          v-model="formData.xiangmu_beizhu"
          type="textarea"
          :rows="4"
          placeholder="请输入项目备注"
          :disabled="mode === 'view'"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>

      <!-- 查看模式下显示额外信息 -->
      <template v-if="mode === 'view' && product">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="步骤数量">
              <el-tag type="warning">{{ product.buzou_count || 0 }} 个</el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类名称">
              <span>{{ product.fenlei_mingcheng }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="创建时间">
              <span>{{ formatDateTime(product.created_at) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="更新时间">
              <span>{{ formatDateTime(product.updated_at) }}</span>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">
          {{ mode === 'view' ? '关闭' : '取消' }}
        </el-button>
        <el-button
          v-if="mode !== 'view'"
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useProductStore } from '@/stores/modules/product'
import { formatDateTime } from '@/utils/date'
import { productTypeOptions, productStatusOptions, priceUnitOptions } from '@/api/modules/product'
import type {
  Product,
  ProductCreate,
  ProductUpdate
} from '@/types/product'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  product?: Product | null
}

const props = withDefaults(defineProps<Props>(), {
  product: null
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 产品管理store
const productStore = useProductStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)

// 表单数据
const formData = reactive<ProductCreate>({
  xiangmu_mingcheng: '',
  xiangmu_bianma: '',
  fenlei_id: '',
  yewu_baojia: 0,
  baojia_danwei: 'yuan',
  banshi_tianshu: 1,
  xiangmu_beizhu: '',
  paixu: 0,
  zhuangtai: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  xiangmu_mingcheng: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 100, message: '项目名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  xiangmu_bianma: [
    // 编码由系统自动生成，不需要验证
  ],
  fenlei_id: [
    { required: true, message: '请选择产品分类', trigger: 'change' }
  ],
  yewu_baojia: [
    { required: true, message: '请输入业务报价', trigger: 'blur' },
    { type: 'number', min: 0, message: '业务报价不能小于0', trigger: 'blur' }
  ],
  baojia_danwei: [
    { required: true, message: '请选择报价单位', trigger: 'change' }
  ],
  banshi_tianshu: [
    { required: true, message: '请输入办事天数', trigger: 'blur' },
    { type: 'number', min: 1, max: 365, message: '办事天数必须在 1 到 365 之间', trigger: 'blur' }
  ],
  paixu: [
    { type: 'number', min: 0, max: 9999, message: '排序号必须在 0 到 9999 之间', trigger: 'blur' }
  ],
  zhuangtai: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  const titles = {
    create: '新增产品项目',
    edit: '编辑产品项目',
    view: '查看产品项目'
  }
  return titles[props.mode]
})

// 使用 storeToRefs 保持响应式
const { categoryOptions } = storeToRefs(productStore)

// 监听器
watch(() => props.visible, async (newVal) => {
  if (newVal) {
    // 加载分类选项
    await productStore.fetchCategoryOptions()

    resetForm()
    if (props.product && (props.mode === 'edit' || props.mode === 'view')) {
      loadProductData()
    }
  }
})

// 方法
const getProductTypeLabel = (type: string) => {
  const option = productTypeOptions.find(opt => opt.value === type)
  return option?.label || type
}

const resetForm = () => {
  Object.assign(formData, {
    xiangmu_mingcheng: '',
    xiangmu_bianma: '',
    fenlei_id: '',
    yewu_baojia: 0,
    baojia_danwei: 'yuan',
    banshi_tianshu: 1,
    xiangmu_beizhu: '',
    paixu: 0,
    zhuangtai: 'active'
  })
  
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const loadProductData = () => {
  if (props.product) {
    Object.assign(formData, {
      xiangmu_mingcheng: props.product.xiangmu_mingcheng,
      xiangmu_bianma: props.product.xiangmu_bianma,
      fenlei_id: props.product.fenlei_id,
      yewu_baojia: props.product.yewu_baojia,
      baojia_danwei: props.product.baojia_danwei,
      banshi_tianshu: props.product.banshi_tianshu,
      xiangmu_beizhu: props.product.xiangmu_beizhu || '',
      paixu: props.product.paixu,
      zhuangtai: props.product.zhuangtai
    })
  }
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (props.mode === 'create') {
      // 创建产品 - 不发送编码字段，让后端自动生成
      const createData: ProductCreate = {
        xiangmu_mingcheng: formData.xiangmu_mingcheng,
        // xiangmu_bianma 由后端自动生成，不发送
        fenlei_id: formData.fenlei_id,
        yewu_baojia: formData.yewu_baojia,
        baojia_danwei: formData.baojia_danwei,
        banshi_tianshu: formData.banshi_tianshu,
        xiangmu_beizhu: formData.xiangmu_beizhu,
        paixu: formData.paixu,
        zhuangtai: formData.zhuangtai
      }
      await productStore.createProduct(createData)
      ElMessage.success('产品项目创建成功')
    } else {
      // 更新产品
      const updateData: ProductUpdate = {
        xiangmu_mingcheng: formData.xiangmu_mingcheng,
        xiangmu_bianma: formData.xiangmu_bianma,
        fenlei_id: formData.fenlei_id,
        yewu_baojia: formData.yewu_baojia,
        baojia_danwei: formData.baojia_danwei,
        banshi_tianshu: formData.banshi_tianshu,
        xiangmu_beizhu: formData.xiangmu_beizhu,
        paixu: formData.paixu,
        zhuangtai: formData.zhuangtai
      }

      await productStore.updateProduct(props.product!.id, updateData)
      ElMessage.success('产品项目更新成功')
    }

    emit('success')
  } catch (error) {
    console.error('提交表单失败:', error)
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(async () => {
  await productStore.fetchCategoryOptions()
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.option-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.option-label {
  flex: 1;
}

.option-tag {
  font-size: 12px;
}

.dialog-footer {
  text-align: right;
}
</style>
