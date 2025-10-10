<template>
  <el-dialog
    :model-value="visible"
    title="分配线索"
    width="500px"
    @close="handleClose"
    @update:model-value="(val: boolean) => emit('update:visible', val)"
  >
    <div v-if="xiansuo" class="xiansuo-info">
      <h4>线索信息</h4>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="线索编号">
          {{ xiansuo.xiansuo_bianma }}
        </el-descriptions-item>
        <el-descriptions-item label="公司名称">
          {{ xiansuo.gongsi_mingcheng }}
        </el-descriptions-item>
        <el-descriptions-item label="联系人">
          {{ xiansuo.lianxi_ren }}
        </el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="getStatusType(xiansuo.xiansuo_zhuangtai)" size="small">
            {{ getStatusText(xiansuo.xiansuo_zhuangtai) }}
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
      <el-form-item label="分配给" prop="fenpei_ren_id">
        <el-select
          v-model="formData.fenpei_ren_id"
          placeholder="请选择销售人员"
          filterable
          style="width: 100%"
          :loading="loadingUsers"
        >
          <el-option
            v-for="user in salesUsers"
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
      
      <el-form-item label="分配备注" prop="beizhu">
        <el-input
          v-model="formData.beizhu"
          type="textarea"
          :rows="3"
          placeholder="请输入分配备注（可选）"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确认分配
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import type { Xiansuo } from '@/types/xiansuo'
import { userApi } from '@/api/modules/user'

// Props
interface Props {
  visible: boolean
  xiansuo: Xiansuo | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Store
const xiansuoStore = useXiansuoStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const loadingUsers = ref(false)
const salesUsers = ref<any[]>([])

const formData = reactive({
  fenpei_ren_id: '',
  beizhu: ''
})

// 表单验证规则
const formRules: FormRules = {
  fenpei_ren_id: [
    { required: true, message: '请选择分配人员', trigger: 'change' }
  ]
}

// 方法
const loadSalesUsers = async () => {
  try {
    loadingUsers.value = true
    // 获取销售人员列表
    const response = await userApi.getUserList({ 
      page: 1,
      size: 100,
      zhuangtai: 'active'
    })
    salesUsers.value = response.items || []
  } catch (error) {
    console.error('加载销售人员列表失败:', error)
    ElMessage.error('加载销售人员列表失败')
    // 使用模拟数据作为备选
    salesUsers.value = [
      { id: '1', xingming: '张销售', yonghu_ming: 'zhang_sales' },
      { id: '2', xingming: '李销售', yonghu_ming: 'li_sales' },
      { id: '3', xingming: '王销售', yonghu_ming: 'wang_sales' }
    ]
  } finally {
    loadingUsers.value = false
  }
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    new: 'info',
    following: 'warning',
    quoted: 'primary',
    success: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    new: '新线索',
    following: '跟进中',
    quoted: '已报价',
    success: '已成交',
    failed: '已失败'
  }
  return textMap[status] || status
}

const handleSubmit = async () => {
  if (!formRef.value || !props.xiansuo) return

  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    await xiansuoStore.assignXiansuo(
      props.xiansuo.id,
      {
        fenpei_ren_id: formData.fenpei_ren_id,
        beizhu: formData.beizhu
      }
    )
    
    ElMessage.success('线索分配成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('分配线索失败:', error)
    ElMessage.error('分配线索失败')
  } finally {
    submitting.value = false
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
  formData.fenpei_ren_id = ''
  formData.beizhu = ''
}

// 监听对话框显示状态
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    loadSalesUsers()
  }
})

// 组件挂载时加载销售人员列表
onMounted(() => {
  loadSalesUsers()
})
</script>

<style scoped>
.xiansuo-info {
  margin-bottom: 20px;
}

.xiansuo-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}
</style>