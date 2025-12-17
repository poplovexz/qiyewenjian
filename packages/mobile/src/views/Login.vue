<template>
  <div class="login-container">
    <div class="login-header">
      <div class="logo-wrapper">
        <div class="logo-circle">
          <van-icon name="manager-o" size="48" color="#fff" />
        </div>
      </div>
      <h1>企业管理系统</h1>
      <p>欢迎回来，请登录您的账号</p>
    </div>

    <div class="login-form">
      <van-form @submit="onSubmit">
        <div class="form-item">
          <div class="input-wrapper">
            <van-icon name="user-o" class="input-icon" />
            <van-field
              v-model="formData.username"
              name="username"
              placeholder="请输入用户名"
              autocomplete="username"
              :border="false"
              :rules="[{ required: true, message: '请输入用户名' }]"
            />
          </div>
        </div>

        <div class="form-item">
          <div class="input-wrapper">
            <van-icon name="lock" class="input-icon" />
            <van-field
              v-model="formData.password"
              type="password"
              name="password"
              placeholder="请输入密码"
              autocomplete="current-password"
              :border="false"
              :rules="[{ required: true, message: '请输入密码' }]"
            />
          </div>
        </div>

        <div class="login-button">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            class="submit-btn"
          >
            <span v-if="!loading">立即登录</span>
          </van-button>
        </div>
      </van-form>

      <div class="login-footer">
        <div class="footer-text">登录即表示同意</div>
        <div class="footer-links">
          <span class="link">用户协议</span>
          <span class="divider">|</span>
          <span class="link">隐私政策</span>
        </div>
      </div>
    </div>

    <!-- 装饰性背景 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
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
  } catch (error: any) {
    console.error('Login error:', error)
    // 错误提示已经在request.ts的拦截器中处理了
    // 这里只需要记录日志即可
    if (error.response?.status === 401) {
      showToast({
        message: '用户名或密码错误',
        type: 'fail'
      })
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 24px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -50px;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: 100px;
  left: -75px;
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 20px;
}

/* 登录头部 */
.login-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.logo-wrapper {
  margin-bottom: 24px;
}

.logo-circle {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.login-header p {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 300;
}

/* 登录表单 */
.login-form {
  flex: 1;
  position: relative;
  z-index: 1;
}

.form-item {
  margin-bottom: 16px;
}

.input-wrapper {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 4px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.input-icon {
  color: #667eea;
  font-size: 20px;
}

:deep(.van-field) {
  padding: 12px 0;
  background: transparent;
}

:deep(.van-field__control) {
  font-size: 15px;
  color: #323233;
}

:deep(.van-field__control::placeholder) {
  color: #969799;
}

.login-button {
  margin-top: 32px;
}

.submit-btn {
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(245, 87, 108, 0.4);
  transition: all 0.3s;
}

.submit-btn:active {
  transform: scale(0.98);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
}

/* 登录页脚 */
.login-footer {
  margin-top: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.footer-text {
  margin-bottom: 8px;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.link {
  color: #fff;
  text-decoration: underline;
  cursor: pointer;
}

.divider {
  color: rgba(255, 255, 255, 0.5);
}
</style>

