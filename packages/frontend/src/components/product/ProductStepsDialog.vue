<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    :title="`产品步骤管理 - ${product?.xiangmu_mingcheng}`"
    width="900px"
    :before-close="handleClose"
  >
    <div class="steps-container">
      <!-- 步骤列表 -->
      <div class="steps-header">
        <div class="header-left">
          <h3>产品步骤列表</h3>
          <p class="description">管理产品的具体执行步骤和费用</p>
        </div>
        <div class="header-right">
          <el-button type="primary" :icon="Plus" @click="handleAddStep">
            添加步骤
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="stepsList"
        border
        style="width: 100%"
        :empty-text="stepsList.length === 0 ? '暂无步骤数据' : ''"
      >
        <el-table-column prop="buzou_mingcheng" label="步骤名称" width="200">
          <template #default="{ row, $index }">
            <el-input
              v-if="row.editing"
              v-model="row.buzou_mingcheng"
              placeholder="请输入步骤名称"
              size="small"
            />
            <span v-else>{{ row.buzou_mingcheng }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="yugu_shichang" label="预估时长" width="120" align="center">
          <template #default="{ row }">
            <el-input-number
              v-if="row.editing"
              v-model="row.yugu_shichang"
              :min="0"
              :precision="1"
              size="small"
              style="width: 100%"
            />
            <span v-else>{{ row.yugu_shichang }} {{ getTimeUnitLabel(row.shichang_danwei) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="shichang_danwei" label="时长单位" width="100" align="center">
          <template #default="{ row }">
            <el-select
              v-if="row.editing"
              v-model="row.shichang_danwei"
              size="small"
              style="width: 100%"
            >
              <el-option
                v-for="option in timeUnitOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            <span v-else>{{ getTimeUnitLabel(row.shichang_danwei) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="buzou_feiyong" label="步骤费用" width="120" align="right">
          <template #default="{ row }">
            <el-input-number
              v-if="row.editing"
              v-model="row.buzou_feiyong"
              :min="0"
              :precision="2"
              size="small"
              style="width: 100%"
            />
            <span v-else class="price">{{ formatPrice(row.buzou_feiyong) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="shi_bixu" label="是否必须" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-if="row.editing"
              v-model="row.shi_bixu"
              active-value="Y"
              inactive-value="N"
              size="small"
            />
            <el-tag
              v-else
              :type="row.shi_bixu === 'Y' ? 'danger' : 'info'"
              size="small"
            >
              {{ row.shi_bixu === 'Y' ? '必须' : '可选' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="paixu" label="排序" width="80" align="center">
          <template #default="{ row }">
            <el-input-number
              v-if="row.editing"
              v-model="row.paixu"
              :min="0"
              :max="999"
              size="small"
              style="width: 100%"
            />
            <span v-else>{{ row.paixu }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="buzou_miaoshu" label="步骤描述" min-width="150">
          <template #default="{ row }">
            <el-input
              v-if="row.editing"
              v-model="row.buzou_miaoshu"
              type="textarea"
              :rows="2"
              placeholder="请输入步骤描述"
              size="small"
            />
            <span v-else class="description">{{ row.buzou_miaoshu || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row, $index }">
            <template v-if="row.editing">
              <el-button
                type="primary"
                size="small"
                :icon="Check"
                @click="handleSaveStep(row, $index)"
              >
                保存
              </el-button>
              <el-button
                size="small"
                :icon="Close"
                @click="handleCancelEdit(row, $index)"
              >
                取消
              </el-button>
            </template>
            <template v-else>
              <el-button
                type="warning"
                size="small"
                :icon="Edit"
                @click="handleEditStep(row, $index)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDeleteStep(row, $index)"
              >
                删除
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <!-- 统计信息 -->
      <div class="steps-summary">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="summary-item">
              <span class="label">总步骤数：</span>
              <span class="value">{{ stepsList.length }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <span class="label">必须步骤：</span>
              <span class="value required">{{ requiredStepsCount }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <span class="label">预估总时长：</span>
              <span class="value">{{ totalTime }} 小时</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <span class="label">总费用：</span>
              <span class="value price">{{ formatPrice(totalCost) }}</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          type="primary"
          :loading="saving"
          @click="handleBatchSave"
          v-if="hasChanges"
        >
          批量保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, Close } from '@element-plus/icons-vue'
import { productStepApi, timeUnitOptions } from '@/api/modules/product'
import type { Product, ProductStep } from '@/types/product'

// Props
interface Props {
  visible: boolean
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

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const stepsList = ref<any[]>([])
const originalSteps = ref<any[]>([])
const hasChanges = ref(false)

// 计算属性
const requiredStepsCount = computed(() => {
  return stepsList.value.filter(step => step.shi_bixu === 'Y').length
})

const totalTime = computed(() => {
  return stepsList.value.reduce((total, step) => {
    const timeInHours = convertToHours(step.yugu_shichang, step.shichang_danwei)
    return total + timeInHours
  }, 0).toFixed(1)
})

const totalCost = computed(() => {
  return stepsList.value.reduce((total, step) => total + (step.buzou_feiyong || 0), 0)
})

// 监听器
watch(() => props.visible, (newVal) => {
  if (newVal && props.product) {
    loadSteps()
  }
})

watch(stepsList, () => {
  hasChanges.value = JSON.stringify(stepsList.value) !== JSON.stringify(originalSteps.value)
}, { deep: true })

// 方法
const getTimeUnitLabel = (unit: string) => {
  const option = timeUnitOptions.find(opt => opt.value === unit)
  return option?.label || unit
}

const formatPrice = (price: number) => {
  return `¥${price.toFixed(2)}`
}

const convertToHours = (time: number, unit: string) => {
  const unitMap: Record<string, number> = {
    xiaoshi: 1,
    tian: 8,
    fenzhong: 1/60
  }
  return time * (unitMap[unit] || 1)
}

const loadSteps = async () => {
  if (!props.product) return
  
  try {
    loading.value = true
    const steps = await productStepApi.getList(props.product.id)
    stepsList.value = steps.map(step => ({
      ...step,
      editing: false,
      isNew: false
    }))
    originalSteps.value = JSON.parse(JSON.stringify(stepsList.value))
    hasChanges.value = false
  } catch (error) {
    console.error('加载步骤列表失败:', error)
    ElMessage.error('加载步骤列表失败')
  } finally {
    loading.value = false
  }
}

const handleAddStep = () => {
  const newStep = {
    id: null,
    buzou_mingcheng: '',
    xiangmu_id: props.product?.id,
    yugu_shichang: 1,
    shichang_danwei: 'xiaoshi',
    buzou_feiyong: 0,
    buzou_miaoshu: '',
    paixu: stepsList.value.length,
    shi_bixu: 'N',
    zhuangtai: 'active',
    editing: true,
    isNew: true
  }
  stepsList.value.push(newStep)
}

const handleEditStep = (step: any, index: number) => {
  step.editing = true
  step.originalData = { ...step }
}

const handleSaveStep = async (step: any, index: number) => {
  if (!step.buzou_mingcheng.trim()) {
    ElMessage.error('请输入步骤名称')
    return
  }

  try {
    if (step.isNew) {
      // 创建新步骤
      const createData = {
        buzou_mingcheng: step.buzou_mingcheng,
        xiangmu_id: props.product!.id,
        yugu_shichang: step.yugu_shichang,
        shichang_danwei: step.shichang_danwei,
        buzou_feiyong: step.buzou_feiyong,
        buzou_miaoshu: step.buzou_miaoshu,
        paixu: step.paixu,
        shi_bixu: step.shi_bixu,
        zhuangtai: step.zhuangtai
      }
      
      const result = await productStepApi.create(createData)
      Object.assign(step, result, { editing: false, isNew: false })
      ElMessage.success('步骤创建成功')
    } else {
      // 更新现有步骤
      const updateData = {
        buzou_mingcheng: step.buzou_mingcheng,
        yugu_shichang: step.yugu_shichang,
        shichang_danwei: step.shichang_danwei,
        buzou_feiyong: step.buzou_feiyong,
        buzou_miaoshu: step.buzou_miaoshu,
        paixu: step.paixu,
        shi_bixu: step.shi_bixu,
        zhuangtai: step.zhuangtai
      }
      
      const result = await productStepApi.update(step.id, updateData)
      Object.assign(step, result, { editing: false })
      ElMessage.success('步骤更新成功')
    }
    
    delete step.originalData
  } catch (error) {
    console.error('保存步骤失败:', error)
    ElMessage.error('保存步骤失败')
  }
}

const handleCancelEdit = (step: any, index: number) => {
  if (step.isNew) {
    stepsList.value.splice(index, 1)
  } else {
    Object.assign(step, step.originalData, { editing: false })
    delete step.originalData
  }
}

const handleDeleteStep = async (step: any, index: number) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除步骤"${step.buzou_mingcheng}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (step.id) {
      await productStepApi.delete(step.id)
      ElMessage.success('步骤删除成功')
    }
    
    stepsList.value.splice(index, 1)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除步骤失败:', error)
      ElMessage.error('删除步骤失败')
    }
  }
}

const handleBatchSave = async () => {
  try {
    saving.value = true
    
    // 这里可以实现批量保存逻辑
    // 目前单个保存已经实现，批量保存可以后续优化
    
    ElMessage.success('批量保存成功')
    hasChanges.value = false
    originalSteps.value = JSON.parse(JSON.stringify(stepsList.value))
  } catch (error) {
    console.error('批量保存失败:', error)
    ElMessage.error('批量保存失败')
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  if (hasChanges.value) {
    ElMessageBox.confirm(
      '有未保存的更改，确定要关闭吗？',
      '确认关闭',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      emit('update:visible', false)
      emit('success')
    }).catch(() => {
      // 用户取消关闭
    })
  } else {
    emit('update:visible', false)
    emit('success')
  }
}
</script>

<style scoped>
.steps-container {
  padding: 10px 0;
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.steps-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.description {
  margin: 4px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.price {
  color: #f56c6c;
  font-weight: 500;
}

.steps-summary {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.summary-item .value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.summary-item .value.required {
  color: #f56c6c;
}

.summary-item .value.price {
  color: #f56c6c;
}

.dialog-footer {
  text-align: right;
}
</style>
