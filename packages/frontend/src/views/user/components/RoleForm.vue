<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      :disabled="mode === 'view'"
    >
      <el-form-item label="角色名称" prop="jiaose_ming">
        <el-input
          v-model="formData.jiaose_ming"
          placeholder="请输入角色名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="角色编码" prop="jiaose_bianma">
        <el-input
          v-model="formData.jiaose_bianma"
          placeholder="请输入角色编码，如：admin、user"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="角色描述" prop="miaoshu">
        <el-input
          v-model="formData.miaoshu"
          type="textarea"
          :rows="3"
          placeholder="请输入角色描述"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="状态" prop="zhuangtai">
        <el-radio-group v-model="formData.zhuangtai">
          <el-radio label="active">启用</el-radio>
          <el-radio label="inactive">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          v-if="mode !== 'view'"
          type="primary" 
          :loading="loading"
          @click="handleSubmit"
        >
          {{ mode === 'create' ? '创建' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import type { Role } from '@/api/modules/role'

interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
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
  jiaose_ming: '',
  jiaose_bianma: '',
  miaoshu: '',
  zhuangtai: 'active'
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  const titleMap = {
    create: '新增角色',
    edit: '编辑角色',
    view: '查看角色'
  }
  return titleMap[props.mode]
})

// 表单验证规则
const formRules: FormRules = {
  jiaose_ming: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  jiaose_bianma: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 2, max: 50, message: '角色编码长度在 2 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '角色编码必须以字母开头，只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  miaoshu: [
    { max: 200, message: '角色描述不能超过 200 个字符', trigger: 'blur' }
  ],
  zhuangtai: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 监听角色数据变化
watch(() => props.role, (newRole) => {
  if (newRole) {
    formData.value = {
      jiaose_ming: newRole.jiaose_ming || '',
      jiaose_bianma: newRole.jiaose_bianma || '',
      miaoshu: newRole.miaoshu || '',
      zhuangtai: newRole.zhuangtai || 'active'
    }
  } else {
    resetForm()
  }
}, { immediate: true })

// 重置表单
const resetForm = () => {
  formData.value = {
    jiaose_ming: '',
    jiaose_bianma: '',
    miaoshu: '',
    zhuangtai: 'active'
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
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // TODO: 调用API创建或更新角色
    if (props.mode === 'create') {
      // await roleApi.createRole(formData.value)
      ElMessage.success('角色创建成功')
    } else {
      // await roleApi.updateRole(props.role!.id, formData.value)
      ElMessage.success('角色更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('角色操作失败:', error)
    ElMessage.error(props.mode === 'create' ? '角色创建失败' : '角色更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
