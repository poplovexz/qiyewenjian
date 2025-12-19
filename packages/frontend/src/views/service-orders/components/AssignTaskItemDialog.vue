<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="分配任务项"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="任务名称">
        <el-input :value="taskItem?.xiangmu_mingcheng" disabled />
      </el-form-item>

      <el-form-item label="任务描述">
        <el-input
          :value="taskItem?.xiangmu_miaoshu"
          type="textarea"
          :rows="3"
          disabled
        />
      </el-form-item>

      <el-form-item label="计划工时">
        <el-input :value="taskItem?.jihua_gongshi + 'h'" disabled />
      </el-form-item>

      <el-form-item label="当前执行人">
        <el-input
          :value="taskItem?.zhixing_ren?.xingming || '未分配'"
          disabled
        />
      </el-form-item>

      <el-form-item label="执行人" prop="zhixingRenId" required>
        <el-select
          v-model="formData.zhixingRenId"
          placeholder="请选择执行人"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="`${user.xingming} (${user.yonghu_ming})`"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { request } from '@/utils/request'
import type { ServiceOrderItem } from '@/stores/modules/serviceOrderManagement'

interface User {
  id: string
  yonghu_ming: string
  xingming: string
}

interface Props {
  modelValue: boolean
  taskItem: ServiceOrderItem | null
  gongdanId: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const users = ref<User[]>([])

const formData = reactive({
  zhixingRenId: ''
})

const rules: FormRules = {
  zhixingRenId: [
    { required: true, message: '请选择执行人', trigger: 'change' }
  ]
}

// 监听对话框打开，加载用户列表
watch(() => props.modelValue, async (newVal) => {
  if (newVal) {
    await loadUsers()
    // 如果任务项已有执行人，设置为默认值
    if (props.taskItem?.zhixing_ren_id) {
      formData.zhixingRenId = props.taskItem.zhixing_ren_id
    } else {
      formData.zhixingRenId = ''
    }
  }
})

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await request.get('/users/')
    users.value = response.items || []
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

// 取消
const handleCancel = () => {
  emit('update:modelValue', false)
  formRef.value?.resetFields()
}

// 确认
const handleConfirm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await request.post(
          `/service-orders/${props.gongdanId}/items/${props.taskItem?.id}/assign`,
          null,
          {
            params: {
              zhixing_ren_id: formData.zhixingRenId
            }
          }
        )
        ElMessage.success('分配任务项成功')
        emit('success')
        emit('update:modelValue', false)
        formRef.value?.resetFields()
      } catch (error) {
        ElMessage.error('分配任务项失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

