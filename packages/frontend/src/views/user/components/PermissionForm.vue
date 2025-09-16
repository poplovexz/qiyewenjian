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
      <el-form-item label="权限名称" prop="quanxian_ming">
        <el-input
          v-model="formData.quanxian_ming"
          placeholder="请输入权限名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="权限编码" prop="quanxian_bianma">
        <el-input
          v-model="formData.quanxian_bianma"
          placeholder="请输入权限编码，如：user:read"
          maxlength="100"
          show-word-limit
        />
        <div class="form-tip">
          权限编码格式：模块:操作，如 user:read、customer:create
        </div>
      </el-form-item>
      
      <el-form-item label="权限描述" prop="miaoshu">
        <el-input
          v-model="formData.miaoshu"
          type="textarea"
          :rows="3"
          placeholder="请输入权限描述"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="资源类型" prop="ziyuan_leixing">
        <el-select
          v-model="formData.ziyuan_leixing"
          placeholder="请选择资源类型"
          style="width: 100%"
        >
          <el-option label="菜单" value="menu">
            <div class="option-item">
              <el-icon><Menu /></el-icon>
              <span>菜单</span>
              <small>页面访问权限</small>
            </div>
          </el-option>
          <el-option label="按钮" value="button">
            <div class="option-item">
              <el-icon><Mouse /></el-icon>
              <span>按钮</span>
              <small>页面操作权限</small>
            </div>
          </el-option>
          <el-option label="接口" value="api">
            <div class="option-item">
              <el-icon><Connection /></el-icon>
              <span>接口</span>
              <small>API访问权限</small>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="资源路径" prop="ziyuan_lujing">
        <el-input
          v-model="formData.ziyuan_lujing"
          placeholder="请输入资源路径"
          maxlength="200"
          show-word-limit
        />
        <div class="form-tip">
          {{ getResourcePathTip() }}
        </div>
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
import { Menu, Mouse, Connection } from '@element-plus/icons-vue'
import type { Permission } from '@/api/modules/permission'

interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  permission?: Permission | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  permission: null
})

const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = ref({
  quanxian_ming: '',
  quanxian_bianma: '',
  miaoshu: '',
  ziyuan_leixing: '',
  ziyuan_lujing: '',
  zhuangtai: 'active'
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  const titleMap = {
    create: '新增权限',
    edit: '编辑权限',
    view: '查看权限'
  }
  return titleMap[props.mode]
})

// 获取资源路径提示
const getResourcePathTip = () => {
  switch (formData.value.ziyuan_leixing) {
    case 'menu':
      return '菜单路径，如：/users、/customers'
    case 'button':
      return '按钮标识，如：user-create-btn、customer-edit-btn'
    case 'api':
      return 'API路径，如：/api/v1/users/*、/api/v1/customers/'
    default:
      return '请先选择资源类型'
  }
}

// 表单验证规则
const formRules: FormRules = {
  quanxian_ming: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  quanxian_bianma: [
    { required: true, message: '请输入权限编码', trigger: 'blur' },
    { min: 2, max: 100, message: '权限编码长度在 2 到 100 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_:]*$/, message: '权限编码必须以字母开头，只能包含字母、数字、下划线和冒号', trigger: 'blur' }
  ],
  miaoshu: [
    { max: 200, message: '权限描述不能超过 200 个字符', trigger: 'blur' }
  ],
  ziyuan_leixing: [
    { required: true, message: '请选择资源类型', trigger: 'change' }
  ],
  ziyuan_lujing: [
    { required: true, message: '请输入资源路径', trigger: 'blur' },
    { max: 200, message: '资源路径不能超过 200 个字符', trigger: 'blur' }
  ],
  zhuangtai: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 重置表单
const resetForm = () => {
  formData.value = {
    quanxian_ming: '',
    quanxian_bianma: '',
    miaoshu: '',
    ziyuan_leixing: '',
    ziyuan_lujing: '',
    zhuangtai: 'active'
  }
  formRef.value?.clearValidate()
}

// 监听权限数据变化
watch(() => props.permission, (newPermission) => {
  if (newPermission) {
    formData.value = {
      quanxian_ming: newPermission.quanxian_ming || '',
      quanxian_bianma: newPermission.quanxian_bianma || '',
      miaoshu: newPermission.miaoshu || '',
      ziyuan_leixing: newPermission.ziyuan_leixing || '',
      ziyuan_lujing: newPermission.ziyuan_lujing || '',
      zhuangtai: newPermission.zhuangtai || 'active'
    }
  } else {
    resetForm()
  }
}, { immediate: true })

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
    
    // TODO: 调用API创建或更新权限
    if (props.mode === 'create') {
      // await permissionApi.createPermission(formData.value)
      ElMessage.success('权限创建成功')
    } else {
      // await permissionApi.updatePermission(props.permission!.id, formData.value)
      ElMessage.success('权限更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('权限操作失败:', error)
    ElMessage.error(props.mode === 'create' ? '权限创建失败' : '权限更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-item small {
  margin-left: auto;
  color: #909399;
}
</style>
