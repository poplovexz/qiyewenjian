<template>
  <view class="login-container">
    <!-- 顶部装饰 -->
    <view class="login-bg">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
    </view>

    <!-- Logo 区域 -->
    <view class="login-header">
      <view class="logo-wrapper">
        <uv-icon name="grid-fill" size="80" color="#1989fa"></uv-icon>
      </view>
      <text class="title">服务人员任务管理</text>
      <text class="subtitle">企业级任务管理解决方案</text>
    </view>

    <!-- 登录表单 -->
    <view class="login-form">
      <uv-form ref="formRef" :model="form" :rules="rules">
        <uv-form-item prop="username">
          <uv-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefixIcon="account"
            prefixIconStyle="color: #909399"
            clearable
            shape="circle"
          ></uv-input>
        </uv-form-item>

        <uv-form-item prop="password">
          <uv-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefixIcon="lock"
            prefixIconStyle="color: #909399"
            clearable
            shape="circle"
          ></uv-input>
        </uv-form-item>

        <view class="form-options">
          <uv-checkbox-group v-model="rememberMe">
            <uv-checkbox name="remember" label="记住密码" size="14"></uv-checkbox>
          </uv-checkbox-group>
          <text class="forget-link">忘记密码?</text>
        </view>

        <uv-button
          type="primary"
          :loading="loading"
          :loadingText="'登录中...'"
          shape="circle"
          customStyle="margin-top: 40rpx; height: 90rpx;"
          @click="handleLogin"
        >
          登 录
        </uv-button>
      </uv-form>

      <view class="login-footer">
        <text class="footer-text">登录即表示同意</text>
        <text class="footer-link">《服务协议》</text>
        <text class="footer-text">和</text>
        <text class="footer-link">《隐私政策》</text>
      </view>
    </view>

    <!-- 版本信息 -->
    <view class="version-info">
      <text>v1.0.0</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const rememberMe = ref<string[]>([])

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!form.username || !form.password) {
    uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const result = await userStore.login(form.username, form.password)
    if (result.success) {
      uni.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1000)
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: #f5f7fa;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 500rpx;
  background: linear-gradient(135deg, #1989fa 0%, #0052d9 100%);

  .circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
  }

  .circle-1 {
    width: 300rpx;
    height: 300rpx;
    top: -100rpx;
    right: -50rpx;
  }

  .circle-2 {
    width: 200rpx;
    height: 200rpx;
    top: 150rpx;
    left: -80rpx;
  }
}

.login-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120rpx;

  .logo-wrapper {
    width: 140rpx;
    height: 140rpx;
    background: #ffffff;
    border-radius: 30rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.1);
    margin-bottom: 30rpx;
  }

  .title {
    font-size: 44rpx;
    color: #ffffff;
    font-weight: bold;
    margin-bottom: 10rpx;
  }

  .subtitle {
    font-size: 26rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

.login-form {
  position: relative;
  z-index: 1;
  margin: 60rpx 30rpx 0;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 50rpx 40rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.05);

  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20rpx;

    .forget-link {
      font-size: 26rpx;
      color: #1989fa;
    }
  }
}

.login-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
  flex-wrap: wrap;

  .footer-text {
    font-size: 24rpx;
    color: #909399;
  }

  .footer-link {
    font-size: 24rpx;
    color: #1989fa;
  }
}

.version-info {
  position: absolute;
  bottom: 40rpx;
  left: 0;
  right: 0;
  text-align: center;

  text {
    font-size: 24rpx;
    color: #c0c4cc;
  }
}
</style>

