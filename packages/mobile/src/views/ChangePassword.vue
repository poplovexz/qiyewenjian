<template>
  <div class="change-password-container">
    <van-nav-bar
      title="修改密码"
      left-arrow
      fixed
      placeholder
      @click-left="onBack"
    />

    <div class="form-container">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="formData.oldPassword"
            type="password"
            name="oldPassword"
            label="旧密码"
            placeholder="请输入旧密码"
            :rules="[{ required: true, message: '请输入旧密码' }]"
          />
          <van-field
            v-model="formData.newPassword"
            type="password"
            name="newPassword"
            label="新密码"
            placeholder="请输入新密码"
            :rules="[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度不能少于6位' }
            ]"
          />
          <van-field
            v-model="formData.confirmPassword"
            type="password"
            name="confirmPassword"
            label="确认密码"
            placeholder="请再次输入新密码"
            :rules="[
              { required: true, message: '请再次输入新密码' },
              { validator: validateConfirmPassword, message: '两次输入的密码不一致' }
            ]"
          />
        </van-cell-group>

        <div class="submit-button">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
          >
            确认修改
          </van-button>
        </div>
      </van-form>

      <div class="tips">
        <van-notice-bar
          left-icon="info-o"
          :scrollable="false"
        >
          <template #default>
            <div class="tips-content">
              <p>密码修改提示：</p>
              <p>1. 密码长度不少于6位</p>
              <p>2. 建议使用字母、数字和符号的组合</p>
              <p>3. 修改成功后需要重新登录</p>
            </div>
          </template>
        </van-notice-bar>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { useUserStore } from '@/stores/user'
import request from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()

const formData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)

// 验证确认密码
const validateConfirmPassword = (value: string) => {
  return value === formData.value.newPassword
}

// 返回
const onBack = () => {
  router.back()
}

// 提交表单
const onSubmit = async () => {
  try {
    loading.value = true

    // 调用修改密码API
    await request({
      url: '/auth/change-password',
      method: 'post',
      data: {
        old_password: formData.value.oldPassword,
        new_password: formData.value.newPassword
      }
    })

    showToast({
      message: '密码修改成功，请重新登录',
      type: 'success'
    })

    // 清除用户信息
    userStore.logout()

    // 延迟跳转到登录页
    setTimeout(() => {
      router.replace('/login')
    }, 1500)
  } catch (error: any) {
    console.error('Change password error:', error)
    showToast({
      message: error.response?.data?.detail || '密码修改失败',
      type: 'fail'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.change-password-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f2f5 0%, #ffffff 100%);
}

.form-container {
  padding: 16px;
}

.submit-button {
  margin-top: 24px;
  padding: 0 16px;
}

.tips {
  margin-top: 24px;
}

.tips-content {
  font-size: 12px;
  line-height: 1.8;
  color: #646566;
}

.tips-content p {
  margin: 0;
}

.tips-content p:first-child {
  font-weight: 500;
  margin-bottom: 4px;
}
</style>

