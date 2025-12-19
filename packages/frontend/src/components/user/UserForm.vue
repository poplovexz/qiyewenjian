<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'create' ? '新增用户' : '编辑用户'"
    width="600px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="80px"
      v-loading="loading"
    >
      <el-form-item label="用户名" prop="yonghu_ming">
        <el-input
          v-model="formData.yonghu_ming"
          placeholder="请输入用户名"
          :disabled="mode === 'edit'"
        />
      </el-form-item>

      <el-form-item label="姓名" prop="xingming">
        <el-input v-model="formData.xingming" placeholder="请输入姓名" />
      </el-form-item>

      <el-form-item label="邮箱" prop="youxiang">
        <el-input v-model="formData.youxiang" placeholder="请输入邮箱" type="email" />
      </el-form-item>

      <el-form-item label="手机号" prop="shouji">
        <el-input v-model="formData.shouji" placeholder="请输入手机号" />
      </el-form-item>

      <el-form-item label="状态" prop="zhuangtai">
        <el-radio-group v-model="formData.zhuangtai">
          <el-radio value="active">启用</el-radio>
          <el-radio value="inactive">禁用</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 创建模式：必须输入密码 -->
      <el-form-item v-if="mode === 'create'" label="密码" prop="mima">
        <el-input v-model="formData.mima" placeholder="请输入密码" type="password" show-password />
      </el-form-item>

      <el-form-item v-if="mode === 'create'" label="确认密码" prop="confirm_password">
        <el-input
          v-model="formData.confirm_password"
          placeholder="请再次输入密码"
          type="password"
          show-password
        />
      </el-form-item>

      <!-- 编辑模式：可选修改密码 -->
      <el-form-item v-if="mode === 'edit'" label="修改密码">
        <el-checkbox v-model="changePassword">修改密码</el-checkbox>
      </el-form-item>

      <el-form-item v-if="mode === 'edit' && changePassword" label="新密码" prop="mima">
        <el-input
          v-model="formData.mima"
          placeholder="请输入新密码"
          type="password"
          show-password
        />
      </el-form-item>

      <el-form-item
        v-if="mode === 'edit' && changePassword"
        label="确认密码"
        prop="confirm_password"
      >
        <el-input
          v-model="formData.confirm_password"
          placeholder="请再次输入新密码"
          type="password"
          show-password
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, withDefaults } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { userApi } from '@/api/modules/user'
import type { UserCreate, UserUpdate } from '@/types/user'

interface Props {
  visible: boolean
  userId?: string
  mode: 'create' | 'edit'
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  userId: undefined,
})
const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const changePassword = ref(false)

// 表单数据
const formData = reactive<UserCreate & { confirm_password?: string }>({
  yonghu_ming: '',
  xingming: '',
  youxiang: '',
  shouji: '',
  zhuangtai: 'active',
  mima: '',
  confirm_password: '',
})

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// 表单验证规则
const formRules: FormRules = {
  yonghu_ming: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  xingming: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' },
  ],
  youxiang: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  shouji: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' },
  ],
  zhuangtai: [{ required: true, message: '请选择状态', trigger: 'change' }],
  mima: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== formData.mima) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    yonghu_ming: '',
    xingming: '',
    youxiang: '',
    shouji: '',
    zhuangtai: 'active',
    mima: '',
    confirm_password: '',
  })

  // 重置修改密码选项
  changePassword.value = false

  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

// 获取用户详情
const fetchUserDetail = async () => {
  if (!props.userId || props.mode === 'create') return

  try {
    loading.value = true
    const userInfo = await userApi.getUserById(props.userId)

    Object.assign(formData, {
      yonghu_ming: userInfo.yonghu_ming,
      xingming: userInfo.xingming,
      youxiang: userInfo.youxiang,
      shouji: userInfo.shouji,
      zhuangtai: userInfo.zhuangtai,
    })
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (props.mode === 'create') {
      // 创建用户
      const createData: UserCreate = {
        yonghu_ming: formData.yonghu_ming,
        xingming: formData.xingming,
        youxiang: formData.youxiang,
        shouji: formData.shouji,
        zhuangtai: formData.zhuangtai,
        mima: formData.mima,
      }

      await userApi.createUser(createData)
      ElMessage.success('用户创建成功')
    } else {
      // 更新用户
      const updateData: UserUpdate = {
        xingming: formData.xingming,
        youxiang: formData.youxiang,
        shouji: formData.shouji,
        zhuangtai: formData.zhuangtai,
      }

      // 如果勾选了修改密码，则包含密码字段
      if (changePassword.value && formData.mima) {
        updateData.mima = formData.mima
      }

      await userApi.updateUser(props.userId!, updateData)
      ElMessage.success('用户更新成功')
    }

    emit('success')
  } catch (error) {
    ElMessage.error(props.mode === 'create' ? '创建用户失败' : '更新用户失败')
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  resetForm()
}

// 监听对话框显示状态
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      if (props.mode === 'edit' && props.userId) {
        fetchUserDetail()
      } else {
        resetForm()
      }
    }
  }
)
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
