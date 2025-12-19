<template>
  <el-dialog
    v-model="dialogVisible"
    title="客户状态管理"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="customer" class="status-dialog">
      <!-- 客户信息 -->
      <div class="customer-info">
        <h4>{{ customer.gongsi_mingcheng }}</h4>
        <p>统一社会信用代码：{{ customer.tongyi_shehui_xinyong_daima }}</p>
        <p>法人代表：{{ customer.faren_xingming }}</p>
      </div>

      <!-- 当前状态 -->
      <div class="current-status">
        <label>当前状态：</label>
        <el-tag :type="getStatusType(customer.kehu_zhuangtai)" size="large">
          {{ getStatusText(customer.kehu_zhuangtai) }}
        </el-tag>
      </div>

      <!-- 状态变更 -->
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="新状态" prop="newStatus">
          <el-select v-model="formData.newStatus" placeholder="选择新状态" style="width: 100%">
            <el-option
              v-for="option in statusOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
              :disabled="option.value === customer.kehu_zhuangtai"
            >
              <div class="status-option">
                <el-tag :type="getStatusType(option.value)" size="small">
                  {{ option.label }}
                </el-tag>
                <span class="status-desc">{{ option.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="变更原因" prop="reason">
          <el-input
            v-model="formData.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入状态变更原因（可选）"
          />
        </el-form-item>

        <!-- 状态变更说明 -->
        <div v-if="formData.newStatus" class="status-description">
          <el-alert
            :title="getStatusDescription(formData.newStatus)"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!formData.newStatus || formData.newStatus === customer?.kehu_zhuangtai"
          @click="handleSubmit"
        >
          确认变更
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useCustomerStore } from '@/stores/modules/customer'
import type { Customer } from '@/api/modules/customer'

interface Props {
  visible: boolean
  customer?: Customer | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  customer: null,
})

const emit = defineEmits<Emits>()

const customerStore = useCustomerStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const formData = ref({
  newStatus: '',
  reason: '',
})

// 状态选项
const statusOptions = [
  {
    value: 'active',
    label: '活跃',
    description: '客户正常服务中，合同有效',
  },
  {
    value: 'renewing',
    label: '续约中',
    description: '客户正在办理续约手续',
  },
  {
    value: 'terminated',
    label: '已终止',
    description: '客户服务已终止，合同到期或主动终止',
  },
]

// 表单验证规则
const formRules: FormRules = {
  newStatus: [{ required: true, message: '请选择新状态', trigger: 'change' }],
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// 监听对话框显示状态
watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      resetForm()
    }
  }
)

// 方法
const resetForm = () => {
  formData.value = {
    newStatus: '',
    reason: '',
  }
  formRef.value?.clearValidate()
}

const getStatusType = (status: string) => {
  const statusMap = {
    active: 'success',
    renewing: 'warning',
    terminated: 'danger',
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '活跃',
    renewing: '续约中',
    terminated: '已终止',
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getStatusDescription = (status: string) => {
  const descriptions = {
    active: '客户将恢复正常服务状态，可以进行所有业务操作',
    renewing: '客户将进入续约流程，需要完成合同续签手续',
    terminated: '客户服务将被终止，相关数据将被归档保存',
  }
  return descriptions[status as keyof typeof descriptions] || ''
}

const handleSubmit = async () => {
  if (!formRef.value || !props.customer) return

  try {
    await formRef.value.validate()

    // 确认对话框
    const confirmMessage = `确定要将客户"${props.customer.gongsi_mingcheng}"的状态从"${getStatusText(props.customer.kehu_zhuangtai)}"变更为"${getStatusText(formData.value.newStatus)}"吗？`

    await ElMessageBox.confirm(confirmMessage, '确认状态变更', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    loading.value = true

    await customerStore.updateCustomerStatus(props.customer.id, formData.value.newStatus)

    emit('success')
    ElMessage.success('客户状态变更成功')
  } catch (error) {
    if (error !== 'cancel') {
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}
</script>

<style scoped>
.status-dialog {
  padding: 10px 0;
}

.customer-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.customer-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.customer-info p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.current-status {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.current-status label {
  font-weight: 500;
  color: #606266;
}

.status-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.status-desc {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.status-description {
  margin-top: 16px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-select-dropdown__item) {
  height: auto;
  padding: 8px 20px;
}
</style>
