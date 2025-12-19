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
          @input="handleNameInput"
        />
      </el-form-item>

      <el-form-item label="角色编码" prop="jiaose_bianma">
        <el-input
          v-model="formData.jiaose_bianma"
          placeholder="自动生成或手动输入，如：admin、user"
          maxlength="50"
          show-word-limit
        >
          <template #append>
            <el-button @click="generateCode" :icon="Refresh"> 重新生成 </el-button>
          </template>
        </el-input>
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>角色编码会根据角色名称自动生成，也可以手动修改</span>
        </div>
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
        <el-button v-if="mode !== 'view'" type="primary" :loading="loading" @click="handleSubmit">
          {{ mode === 'create' ? '创建' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Refresh, InfoFilled } from '@element-plus/icons-vue'
import type { Role } from '@/api/modules/role'
import { roleApi } from '@/api/modules/user'

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
  role: null,
})

const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = ref({
  jiaose_ming: '',
  jiaose_bianma: '',
  miaoshu: '',
  zhuangtai: 'active',
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

const dialogTitle = computed(() => {
  const titleMap = {
    create: '新增角色',
    edit: '编辑角色',
    view: '查看角色',
  }
  return titleMap[props.mode]
})

// 表单验证规则
const formRules: FormRules = {
  jiaose_ming: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  jiaose_bianma: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 2, max: 50, message: '角色编码长度在 2 到 50 个字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/,
      message: '角色编码必须以字母开头，只能包含字母、数字和下划线',
      trigger: 'blur',
    },
  ],
  miaoshu: [{ max: 200, message: '角色描述不能超过 200 个字符', trigger: 'blur' }],
  zhuangtai: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

// 中文拼音映射表（常用字）
const pinyinMap: Record<string, string> = {
  业: 'ye',
  务: 'wu',
  员: 'yuan',
  财: 'cai',
  管: 'guan',
  理: 'li',
  销: 'xiao',
  售: 'shou',
  客: 'ke',
  服: 'fu',
  技: 'ji',
  术: 'shu',
  产: 'chan',
  品: 'pin',
  运: 'yun',
  营: 'ying',
  人: 'ren',
  事: 'shi',
  行: 'xing',
  政: 'zheng',
  总: 'zong',
  经: 'jing',
  副: 'fu',
  主: 'zhu',
  专: 'zhuan',
  助: 'zhu',
}

// 生成角色编码
const generateCode = () => {
  const name = formData.value.jiaose_ming.trim()
  if (!name) {
    ElMessage.warning('请先输入角色名称')
    return
  }

  let code = ''

  // 尝试使用拼音映射
  for (const char of name) {
    if (pinyinMap[char]) {
      code += pinyinMap[char]
    } else if (/[a-zA-Z0-9]/.test(char)) {
      // 保留英文和数字
      code += char.toLowerCase()
    }
  }

  // 如果没有生成任何编码，使用默认规则
  if (!code) {
    // 提取英文和数字
    code = name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase()

    // 如果还是空的，使用时间戳
    if (!code) {
      code = 'role_' + Date.now()
    }
  }

  // 清理编码：只保留字母、数字和下划线
  code = code.replace(/[^a-z0-9_]/g, '')

  // 确保以字母开头
  if (!/^[a-z]/.test(code)) {
    code = 'role_' + code
  }

  formData.value.jiaose_bianma = code
  ElMessage.success('角色编码已生成: ' + code)
}

// 处理角色名称输入
const handleNameInput = () => {
  // 只在创建模式且编码为空时自动生成
  if (props.mode === 'create' && !formData.value.jiaose_bianma) {
    generateCode()
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    jiaose_ming: '',
    jiaose_bianma: '',
    miaoshu: '',
    zhuangtai: 'active',
  }
  formRef.value?.clearValidate()
}

// 监听角色数据变化
watch(
  () => props.role,
  (newRole) => {
    if (newRole) {
      formData.value = {
        jiaose_ming: newRole.jiaose_ming || '',
        jiaose_bianma: newRole.jiaose_bianma || '',
        miaoshu: newRole.miaoshu || '',
        zhuangtai: newRole.zhuangtai || 'active',
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

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

    // 调用API创建或更新角色
    if (props.mode === 'create') {
      await roleApi.createRole(formData.value)
      ElMessage.success('角色创建成功')
    } else {
      await roleApi.updateRole(props.role!.id, formData.value)
      ElMessage.success('角色更新成功')
    }

    emit('success')
    handleClose()
  } catch (error) {
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

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  font-size: 14px;
}
</style>
