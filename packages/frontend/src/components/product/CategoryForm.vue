<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    :title="dialogTitle"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      v-loading="submitting"
    >
      <el-form-item label="分类名称" prop="fenlei_mingcheng">
        <el-input
          v-model="formData.fenlei_mingcheng"
          placeholder="请输入分类名称"
          :disabled="mode === 'view'"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="分类编码" prop="fenlei_bianma">
        <el-input
          v-model="formData.fenlei_bianma"
          placeholder="请输入分类编码"
          :disabled="mode === 'view'"
          maxlength="50"
          show-word-limit
        />
        <div class="form-tip">编码用于系统内部标识，建议使用英文和数字</div>
      </el-form-item>

      <el-form-item label="产品类型" prop="chanpin_leixing">
        <el-select
          v-model="formData.chanpin_leixing"
          placeholder="请选择产品类型"
          :disabled="mode === 'view'"
          style="width: 100%"
        >
          <el-option
            v-for="option in productTypeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          >
            <div class="option-content">
              <span class="option-label">{{ option.label }}</span>
              <span class="option-desc">{{ option.description }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="排序号" prop="paixu">
        <el-input-number
          v-model="formData.paixu"
          :min="0"
          :max="9999"
          :disabled="mode === 'view'"
          style="width: 200px"
        />
        <div class="form-tip">数字越小排序越靠前</div>
      </el-form-item>

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

      <el-form-item label="分类描述" prop="miaoshu">
        <el-input
          v-model="formData.miaoshu"
          type="textarea"
          :rows="4"
          placeholder="请输入分类描述"
          :disabled="mode === 'view'"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>

      <!-- 查看模式下显示额外信息 -->
      <template v-if="mode === 'view' && category">
        <el-form-item label="项目数量">
          <el-tag type="info">{{ category.xiangmu_count || 0 }} 个</el-tag>
        </el-form-item>
        <el-form-item label="创建时间">
          <span>{{ formatDateTime(category.created_at) }}</span>
        </el-form-item>
        <el-form-item label="更新时间">
          <span>{{ formatDateTime(category.updated_at) }}</span>
        </el-form-item>
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
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useProductStore } from '@/stores/modules/product'
import { formatDateTime } from '@/utils/date'
import { productTypeOptions, productStatusOptions } from '@/api/modules/product'
import type { 
  ProductCategory, 
  ProductCategoryCreate, 
  ProductCategoryUpdate 
} from '@/types/product'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  category?: ProductCategory | null
}

const props = withDefaults(defineProps<Props>(), {
  category: null
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
const formData = reactive<ProductCategoryCreate>({
  fenlei_mingcheng: '',
  fenlei_bianma: '',
  chanpin_leixing: 'zengzhi',
  miaoshu: '',
  paixu: 0,
  zhuangtai: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  fenlei_mingcheng: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '分类名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  fenlei_bianma: [
    { required: true, message: '请输入分类编码', trigger: 'blur' },
    { min: 1, max: 50, message: '分类编码长度在 1 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '分类编码只能包含字母、数字、下划线和横线', trigger: 'blur' }
  ],
  chanpin_leixing: [
    { required: true, message: '请选择产品类型', trigger: 'change' }
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
    create: '新增产品分类',
    edit: '编辑产品分类',
    view: '查看产品分类'
  }
  return titles[props.mode]
})

// 监听器
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
    if (props.category && (props.mode === 'edit' || props.mode === 'view')) {
      loadCategoryData()
    }
  }
})

// 方法
const resetForm = () => {
  Object.assign(formData, {
    fenlei_mingcheng: '',
    fenlei_bianma: '',
    chanpin_leixing: 'zengzhi',
    miaoshu: '',
    paixu: 0,
    zhuangtai: 'active'
  })
  
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const loadCategoryData = () => {
  if (props.category) {
    Object.assign(formData, {
      fenlei_mingcheng: props.category.fenlei_mingcheng,
      fenlei_bianma: props.category.fenlei_bianma,
      chanpin_leixing: props.category.chanpin_leixing,
      miaoshu: props.category.miaoshu || '',
      paixu: props.category.paixu,
      zhuangtai: props.category.zhuangtai
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
      // 创建分类
      await productStore.createCategory(formData)
      ElMessage.success('产品分类创建成功')
    } else {
      // 更新分类
      const updateData: ProductCategoryUpdate = {
        fenlei_mingcheng: formData.fenlei_mingcheng,
        fenlei_bianma: formData.fenlei_bianma,
        chanpin_leixing: formData.chanpin_leixing,
        miaoshu: formData.miaoshu,
        paixu: formData.paixu,
        zhuangtai: formData.zhuangtai
      }
      
      await productStore.updateCategory(props.category!.id, updateData)
      ElMessage.success('产品分类更新成功')
    }
    
    emit('success')
  } catch (error) {
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.option-content {
  display: flex;
  flex-direction: column;
}

.option-label {
  font-weight: 500;
}

.option-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.dialog-footer {
  text-align: right;
}
</style>
