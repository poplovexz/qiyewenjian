<template>
  <div class="login-container">
    <div class="login-header">
      <h1>服务人员任务管理</h1>
      <p>欢迎登录</p>
    </div>

    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="formData.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          autocomplete="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        />
        <van-field
          v-model="formData.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          autocomplete="current-password"
          :rules="[{ required: true, message: '请输入密码' }]"
        />
      </van-cell-group>

      <div class="login-button">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import { login as loginApi, getCurrentUser } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const formData = ref({
  username: '',
  password: ''
})

const loading = ref(false)

const onSubmit = async () => {
  try {
    loading.value = true

    // 调用登录API
    const res: any = await loginApi({
      yonghu_ming: formData.value.username,
      mima: formData.value.password
    })

    // 保存Token和用户信息
    userStore.setToken(res.token.access_token)
    userStore.setUserInfo(res.user)

    showToast({
      message: '登录成功',
      type: 'success'
    })

    // 跳转到首页
    router.push('/home')
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 20px 20px;
}

.login-header {
  text-align: center;
  color: white;
  margin-bottom: 60px;
}

.login-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 16px;
  opacity: 0.9;
}

.login-button {
  margin: 30px 16px;
}
</style>

