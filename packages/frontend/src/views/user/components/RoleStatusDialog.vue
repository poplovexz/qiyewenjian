<template>
  <el-dialog
    v-model="dialogVisible"
    title="状态管理"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="role" class="status-dialog">
      <div class="role-info">
        <h4>角色信息</h4>
        <p><strong>角色名称：</strong>{{ role.jiaose_ming }}</p>
        <p><strong>角色编码：</strong>{{ role.jiaose_bianma }}</p>
        <p><strong>当前状态：</strong>
          <el-tag 
            :type="role.zhuangtai === 'active' ? 'success' : 'danger'"
            size="small"
          >
            {{ role.zhuangtai === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </p>
      </div>
      
      <el-divider />
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="新状态" prop="zhuangtai">
          <el-radio-group v-model="formData.zhuangtai">
            <el-radio label="active">
              <div class="status-option">
                <el-icon color="#67c23a"><CircleCheck /></el-icon>
                <span>启用</span>
                <small>角色可正常使用，用户可被分配此角色</small>
              </div>
            </el-radio>
            <el-radio label="inactive">
              <div class="status-option">
                <el-icon color="#f56c6c"><CircleClose /></el-icon>
                <span>禁用</span>
                <small>角色被禁用，已分配的用户将失去此角色权限</small>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="变更原因" prop="reason">
          <el-input
            v-model="formData.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入状态变更原因（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <div v-if="role.zhuangtai !== formData.zhuangtai" class="warning-info">
        <el-alert
          :title="getWarningTitle()"
          :description="getWarningDescription()"
          type="warning"
          show-icon
          :closable="false"
        />
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          :loading="loading"
          :disabled="role?.zhuangtai === formData.zhuangtai"
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
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import type { Role } from '@/api/modules/role'

interface Props {
  visible: boolean
  role?: Role | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  role: null
})

const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = ref({
  zhuangtai: 'active',
  reason: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 表单验证规则
const formRules: FormRules = {
  zhuangtai: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  reason: [
    { max: 200, message: '变更原因不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 获取警告标题
const getWarningTitle = () => {
  if (!props.role) return ''
  
  if (props.role.zhuangtai === 'active' && formData.value.zhuangtai === 'inactive') {
    return '禁用角色警告'
  } else if (props.role.zhuangtai === 'inactive' && formData.value.zhuangtai === 'active') {
    return '启用角色提醒'
  }
  return ''
}

// 获取警告描述
const getWarningDescription = () => {
  if (!props.role) return ''
  
  if (props.role.zhuangtai === 'active' && formData.value.zhuangtai === 'inactive') {
    return '禁用此角色后，所有拥有此角色的用户将立即失去相关权限，可能影响其正常使用系统。请确认是否继续？'
  } else if (props.role.zhuangtai === 'inactive' && formData.value.zhuangtai === 'active') {
    return '启用此角色后，所有拥有此角色的用户将重新获得相关权限。'
  }
  return ''
}

// 监听角色变化
watch(() => props.role, (newRole) => {
  if (newRole) {
    formData.value = {
      zhuangtai: newRole.zhuangtai || 'active',
      reason: ''
    }
  }
}, { immediate: true })

// 重置表单
const resetForm = () => {
  formData.value = {
    zhuangtai: 'active',
    reason: ''
  }
  formRef.value?.clearValidate()
}

// 处理关闭
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value || !props.role) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 调用API更新角色状态
    const response = await fetch(`/api/v1/roles/${props.role.id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        zhuangtai: formData.value.zhuangtai,
        reason: formData.value.reason
      })
    })

    if (!response.ok) {
      throw new Error('更新角色状态失败')
    }

    ElMessage.success('角色状态更新成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('角色状态更新失败:', error)
    ElMessage.error('角色状态更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.status-dialog {
  max-height: 500px;
  overflow-y: auto;
}

.role-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.role-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.role-info p {
  margin: 8px 0;
  color: #606266;
}

.status-option {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 8px 0;
}

.status-option span {
  font-weight: 500;
  color: #303133;
}

.status-option small {
  color: #909399;
  font-size: 12px;
}

.warning-info {
  margin-top: 16px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-radio) {
  display: block;
  margin-bottom: 16px;
  height: auto;
  line-height: normal;
}

:deep(.el-radio__label) {
  padding-left: 8px;
}
</style>
