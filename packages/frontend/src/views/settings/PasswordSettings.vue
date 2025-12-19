<template>
  <div class="password-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>

      <el-alert
        title="密码安全提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <ul style="margin: 0; padding-left: 20px">
          <li>密码长度至少6位</li>
          <li>建议使用字母、数字和特殊字符的组合</li>
          <li>不要使用过于简单的密码</li>
          <li>定期更换密码以保证账号安全</li>
        </ul>
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        style="max-width: 600px"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="formData.old_password"
            type="password"
            placeholder="请输入旧密码"
            show-password
            autocomplete="off"
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="formData.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
            autocomplete="off"
          />
        </el-form-item>

        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="formData.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            autocomplete="off"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            修改密码
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { changePassword, type PasswordChange } from '@/api/modules/settings'

const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const formData = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 验证确认密码
const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== formData.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules: FormRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度在 6 到 100 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const data: PasswordChange = {
          old_password: formData.old_password,
          new_password: formData.new_password
        }
        await changePassword(data)
        ElMessage.success('密码修改成功，请重新登录')
        // 清空表单
        handleReset()
        // TODO: 可以选择自动退出登录
        // setTimeout(() => {
        //   router.push('/login')
        // }, 1500)
      } catch (error: unknown) {
        const err = error as { message?: string }
        ElMessage.error(err.message || '密码修改失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
}
</script>

<style scoped lang="scss">
.password-settings {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}
</style>
