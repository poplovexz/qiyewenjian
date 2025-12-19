<template>
  <el-dialog
    :model-value="visible"
    title="取消工单"
    width="500px"
    @update:model-value="emit('update:visible', $event)"
    @close="handleClose"
  >
    <div v-if="order" class="order-info">
      <el-alert
        title="警告"
        type="warning"
        description="取消工单后，工单状态将变为已取消，无法恢复。请谨慎操作！"
        show-icon
        :closable="false"
        style="margin-bottom: 20px"
      />

      <h4>工单信息</h4>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="工单编号">
          {{ order.gongdan_bianhao }}
        </el-descriptions-item>
        <el-descriptions-item label="工单标题">
          {{ order.gongdan_biaoti }}
        </el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="getStatusType(order.gongdan_zhuangtai)">
            {{ serviceOrderStore.statusMap[order.gongdan_zhuangtai] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前进度">
          <el-progress
            :percentage="order.progress_percentage"
            :color="getProgressColor(order.progress_percentage)"
            :stroke-width="8"
          />
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      style="margin-top: 20px"
    >
      <el-form-item label="取消原因" prop="cancel_reason">
        <el-select
          v-model="formData.cancel_reason"
          placeholder="请选择取消原因"
          style="width: 100%"
          @change="handleReasonChange"
        >
          <el-option label="客户要求取消" value="客户要求取消" />
          <el-option label="合同已终止" value="合同已终止" />
          <el-option label="服务内容变更" value="服务内容变更" />
          <el-option label="技术问题无法解决" value="技术问题无法解决" />
          <el-option label="资源不足" value="资源不足" />
          <el-option label="其他原因" value="其他原因" />
        </el-select>
      </el-form-item>

      <el-form-item label="详细说明" prop="cancel_detail" :rules="detailRules">
        <el-input
          v-model="formData.cancel_detail"
          type="textarea"
          :rows="4"
          placeholder="请详细说明取消原因，包括具体情况、影响范围等"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="danger" @click="handleSubmit" :loading="loading"> 确认取消工单 </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useServiceOrderStore, type ServiceOrder } from '@/stores/modules/serviceOrderManagement'

// Props
interface Props {
  visible: boolean
  order: ServiceOrder | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Store
const serviceOrderStore = useServiceOrderStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = reactive({
  cancel_reason: '',
  cancel_detail: '',
})

// 表单验证规则
const formRules: FormRules = {
  cancel_reason: [{ required: true, message: '请选择取消原因', trigger: 'change' }],
}

const detailRules = computed(() => {
  const rules = [
    { required: true, message: '请输入详细说明', trigger: 'blur' },
    { min: 10, message: '详细说明至少10个字符', trigger: 'blur' },
  ]

  // 如果选择"其他原因"，要求更详细的说明
  if (formData.cancel_reason === '其他原因') {
    rules.push({
      min: 20,
      message: '选择其他原因时，请提供至少20个字符的详细说明',
      trigger: 'blur',
    })
  }

  return rules
})

// 方法
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    created: 'info',
    assigned: 'warning',
    in_progress: 'primary',
    pending_review: 'warning',
    completed: 'success',
    cancelled: 'danger',
  }
  return typeMap[status] || 'info'
}

const getProgressColor = (percentage: number) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const handleReasonChange = (reason: string) => {
  // 根据选择的原因预填充详细说明
  const templates: Record<string, string> = {
    客户要求取消: '客户主动要求取消此工单，原因：',
    合同已终止: '相关合同已终止，工单无法继续执行。',
    服务内容变更: '服务内容发生重大变更，需要重新制定工单。',
    技术问题无法解决: '遇到技术问题无法在预期时间内解决：',
    资源不足: '当前资源不足，无法按时完成工单：',
    其他原因: '其他原因：',
  }

  if (templates[reason]) {
    formData.cancel_detail = templates[reason]
  }
}

const handleSubmit = async () => {
  if (!formRef.value || !props.order) return

  try {
    await formRef.value.validate()

    // 确认对话框
    await ElMessageBox.confirm(
      `确认取消工单"${props.order.gongdan_biaoti}"？\n\n取消原因：${formData.cancel_reason}\n\n此操作不可恢复！`,
      '确认取消工单',
      {
        type: 'error',
        confirmButtonText: '确认取消',
        cancelButtonText: '我再想想',
        confirmButtonClass: 'el-button--danger',
      }
    )

    loading.value = true

    const cancelReason = `${formData.cancel_reason}：${formData.cancel_detail}`

    await serviceOrderStore.cancelServiceOrder(props.order.id, cancelReason)

    emit('success')
  } catch (error) {
    if (error !== 'cancel') {
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }

  Object.assign(formData, {
    cancel_reason: '',
    cancel_detail: '',
  })
}

// 监听
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      resetForm()
    }
  }
)
</script>

<style scoped>
.order-info {
  margin-bottom: 20px;
}

.order-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.dialog-footer {
  text-align: right;
}
</style>
