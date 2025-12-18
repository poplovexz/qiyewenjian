<template>
  <el-dialog
    v-model="dialogVisible"
    title="服务记录管理"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="service-record-content">
      <p>服务记录管理功能正在开发中...</p>
      <p>客户ID: {{ customerId }}</p>
      <p>客户名称: {{ customerName }}</p>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleSuccess">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// Props
interface Props {
  visible: boolean
  customerId: string
  customerName: string
  record?: any
  mode?: 'view' | 'edit' | 'create'
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  customerId: '',
  customerName: '',
  record: null,
  mode: 'view',
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 响应式数据
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// 方法
const handleClose = () => {
  dialogVisible.value = false
}

const handleSuccess = () => {
  emit('success')
  handleClose()
}

// 监听props变化
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      // 对话框打开时的逻辑
    }
  }
)
</script>

<style scoped>
.service-record-content {
  padding: 20px;
  text-align: center;
}

.dialog-footer {
  text-align: right;
}
</style>
