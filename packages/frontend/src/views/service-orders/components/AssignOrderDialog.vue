<template>
  <el-dialog
    v-model="visible"
    title="分配工单"
    width="500px"
    @close="handleClose"
  >
    <div v-if="order" class="order-info">
      <h4>工单信息</h4>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="工单编号">
          {{ order.gongdan_bianhao }}
        </el-descriptions-item>
        <el-descriptions-item label="工单标题">
          {{ order.gongdan_biaoti }}
        </el-descriptions-item>
        <el-descriptions-item label="服务类型">
          {{ serviceOrderStore.serviceTypeMap[order.fuwu_leixing] }}
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(order.youxian_ji)" size="small">
            {{ serviceOrderStore.priorityMap[order.youxian_ji] }}
          </el-tag>
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
      <el-form-item label="执行人" prop="zhixing_ren_id">
        <el-select
          v-model="formData.zhixing_ren_id"
          placeholder="请选择执行人"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.xingming"
            :value="user.id"
          >
            <div style="display: flex; justify-content: space-between">
              <span>{{ user.xingming }}</span>
              <span style="color: #8492a6; font-size: 13px">{{ user.yonghu_ming }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="分配备注" prop="fenpei_beizhu">
        <el-input
          v-model="formData.fenpei_beizhu"
          type="textarea"
          :rows="3"
          placeholder="请输入分配备注（可选）"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确认分配
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
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
const users = ref([])

const formData = reactive({
  zhixing_ren_id: '',
  fenpei_beizhu: ''
})

// 表单验证规则
const formRules: FormRules = {
  zhixing_ren_id: [
    { required: true, message: '请选择执行人', trigger: 'change' }
  ]
}

// 方法
const loadUsers = async () => {
  try {
    // 加载用户列表
    // users.value = await userStore.fetchUsers({ role: 'accountant' })
    
    // 模拟数据
    users.value = [
      { id: '1', xingming: '张会计', yonghu_ming: 'zhang_kuaiji' },
      { id: '2', xingming: '李会计', yonghu_ming: 'li_kuaiji' },
      { id: '3', xingming: '王会计', yonghu_ming: 'wang_kuaiji' }
    ]
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const getPriorityType = (priority: string) => {
  const typeMap: Record<string, string> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    urgent: 'danger'
  }
  return typeMap[priority] || 'info'
}

const handleSubmit = async () => {
  if (!formRef.value || !props.order) return

  try {
    await formRef.value.validate()
    
    loading.value = true
    
    await serviceOrderStore.assignServiceOrder(
      props.order.id,
      formData.zhixing_ren_id,
      formData.fenpei_beizhu
    )
    
    emit('success')
  } catch (error) {
    console.error('分配工单失败:', error)
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
    zhixing_ren_id: '',
    fenpei_beizhu: ''
  })
}

// 监听
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadUsers()
  }
})

// 生命周期
onMounted(() => {
  loadUsers()
})
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
