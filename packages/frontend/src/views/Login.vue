<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="background-wrapper">
      <!-- 渐变背景 -->
      <div class="gradient-bg"></div>

      <!-- 动态网格 -->
      <div class="grid-overlay"></div>

      <!-- 浮动粒子 -->
      <div class="particles">
        <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>

      <!-- 光晕效果 -->
      <div class="glow-orb glow-orb-1"></div>
      <div class="glow-orb glow-orb-2"></div>
      <div class="glow-orb glow-orb-3"></div>
    </div>

    <!-- 登录卡片容器 -->
    <div class="login-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-logo">
            <div class="logo-circle">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <h1 class="brand-title">代理记账营运内部系统</h1>
          <p class="brand-subtitle">专业 · 高效 · 智能</p>
          <div class="brand-features">
            <div class="feature-item">
              <el-icon class="feature-icon"><Check /></el-icon>
              <span>智能化流程管理</span>
            </div>
            <div class="feature-item">
              <el-icon class="feature-icon"><Check /></el-icon>
              <span>数据安全保障</span>
            </div>
            <div class="feature-item">
              <el-icon class="feature-icon"><Check /></el-icon>
              <span>7×24小时服务</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-section">
        <div class="form-container">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账户以继续</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="yonghu_ming" class="form-item">
              <label class="input-label">用户名</label>
              <el-input
                v-model="loginForm.yonghu_ming"
                placeholder="请输入用户名"
                size="large"
                clearable
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="mima" class="form-item">
              <label class="input-label">密码</label>
              <el-input
                v-model="loginForm.mima"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password
                clearable
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe" class="remember-checkbox">
                记住我
              </el-checkbox>
              <a href="#" class="forgot-link" @click.prevent>忘记密码？</a>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="isLoading"
              class="login-btn"
              @click="handleLogin"
            >
              <span v-if="!isLoading">登 录</span>
              <span v-else>登录中...</span>
            </el-button>

            <div v-if="error" class="error-alert">
              <el-icon class="error-icon"><Warning /></el-icon>
              <span>{{ error }}</span>
            </div>
          </el-form>

          <div class="form-footer">
            <p class="footer-text">
              还没有账户？<a href="#" class="contact-link" @click.prevent>联系管理员</a>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部版权 -->
    <div class="page-footer">
      <p>© 2024 代理记账营运内部系统. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElForm, ElMessage } from 'element-plus'
import { User, Lock, Warning, Check } from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'
import type { LoginRequest } from '@/api/auth'

// 组合式函数
const { login, isLoading, isAuthenticated } = useAuth()

// 表单引用
const loginFormRef = ref<InstanceType<typeof ElForm>>()

// 记住我状态
const rememberMe = ref(false)

// 错误信息
const error = ref('')

// 登录表单数据
const loginForm = reactive<LoginRequest>({
  yonghu_ming: '',
  mima: ''
})

// 表单验证规则
const loginRules = {
  yonghu_ming: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  mima: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ]
}

// 粒子样式生成
const getParticleStyle = (index: number) => {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const animationDuration = Math.random() * 20 + 10
  const animationDelay = Math.random() * 5

  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDuration: `${animationDuration}s`,
    animationDelay: `${animationDelay}s`
  }
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    error.value = ''
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    await login(loginForm)

    if (rememberMe.value) {
      localStorage.setItem('rememberMe', 'true')
      localStorage.setItem('username', loginForm.yonghu_ming)
    } else {
      localStorage.removeItem('rememberMe')
      localStorage.removeItem('username')
    }
  } catch (err: any) {
    console.error('登录失败:', err)
    error.value = err.message || '登录失败，请检查用户名和密码'
  }
}

// 组件挂载时检查是否已登录
onMounted(() => {
  if (isAuthenticated.value) {
    ElMessage.info('您已经登录，正在跳转...')
  }

  // 检查记住我
  const remembered = localStorage.getItem('rememberMe')
  if (remembered === 'true') {
    rememberMe.value = true
    const username = localStorage.getItem('username')
    if (username) {
      loginForm.yonghu_ming = username
    }
  }
})
</script>

<style scoped>
/* ==================== 容器和背景 ==================== */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #0f172a;
}

/* 背景包装器 */
.background-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

/* 渐变背景 */
.gradient-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.9;
}

/* 网格覆盖层 */
.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

/* 浮动粒子 */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: particleFloat linear infinite;
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) scale(1);
    opacity: 0;
  }
}

/* 光晕效果 */
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orbFloat 15s ease-in-out infinite;
}

.glow-orb-1 {
  width: 400px;
  height: 400px;
  background: #667eea;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.glow-orb-2 {
  width: 500px;
  height: 500px;
  background: #764ba2;
  bottom: -150px;
  right: -150px;
  animation-delay: 5s;
}

.glow-orb-3 {
  width: 350px;
  height: 350px;
  background: #f093fb;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 10s;
}

@keyframes orbFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* ==================== 登录包装器 ==================== */
.login-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-height: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 100px rgba(102, 126, 234, 0.2);
  overflow: hidden;
  animation: slideUp 0.8s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== 品牌区域 ==================== */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
}

.brand-logo {
  margin-bottom: 30px;
  animation: fadeInDown 0.8s ease-out 0.2s both;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logo-circle {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.logo-circle:hover {
  transform: scale(1.05) rotate(5deg);
}

.logo-circle svg {
  width: 50px;
  height: 50px;
  color: white;
}

.brand-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 15px 0;
  line-height: 1.2;
  animation: fadeInDown 0.8s ease-out 0.4s both;
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0 0 40px 0;
  font-weight: 300;
  letter-spacing: 2px;
  animation: fadeInDown 0.8s ease-out 0.6s both;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1rem;
  opacity: 0.95;
  animation: fadeInLeft 0.8s ease-out both;
}

.feature-item:nth-child(1) {
  animation-delay: 0.8s;
}

.feature-item:nth-child(2) {
  animation-delay: 1s;
}

.feature-item:nth-child(3) {
  animation-delay: 1.2s;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 0.95;
    transform: translateX(0);
  }
}

.feature-icon {
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

/* ==================== 表单区域 ==================== */
.form-section {
  flex: 1;
  padding: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 40px;
  animation: fadeInUp 0.8s ease-out 0.4s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 10px 0;
}

.form-subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0;
}

/* 表单样式 */
.login-form {
  animation: fadeInUp 0.8s ease-out 0.6s both;
}

.form-item {
  margin-bottom: 24px;
}

.input-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
}

.form-item :deep(.el-input) {
  --el-input-height: 48px;
}

.form-item :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-item :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.form-item :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
  border-color: #667eea;
}

.form-item :deep(.el-input__inner) {
  font-size: 0.95rem;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.remember-checkbox :deep(.el-checkbox__label) {
  font-size: 0.875rem;
  color: #64748b;
}

.forgot-link {
  font-size: 0.875rem;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.forgot-link:hover {
  color: #764ba2;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 50px;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.login-btn:active {
  transform: translateY(0);
}

/* 错误提示 */
.error-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 20px;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.error-icon {
  font-size: 18px;
}

/* 表单底部 */
.form-footer {
  margin-top: 30px;
  text-align: center;
  animation: fadeInUp 0.8s ease-out 0.8s both;
}

.footer-text {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.contact-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
  transition: all 0.3s ease;
}

.contact-link:hover {
  color: #764ba2;
}

/* 页面底部 */
.page-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 1;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
}

.page-footer p {
  margin: 0;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 1024px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 500px;
  }

  .brand-section {
    padding: 40px;
    min-height: 300px;
  }

  .brand-title {
    font-size: 1.75rem;
  }

  .brand-subtitle {
    font-size: 1rem;
  }

  .form-section {
    padding: 40px;
  }
}

@media (max-width: 640px) {
  .login-container {
    padding: 1rem;
  }

  .login-wrapper {
    border-radius: 16px;
    min-height: auto;
  }

  .brand-section {
    padding: 30px 20px;
    min-height: 250px;
  }

  .brand-title {
    font-size: 1.5rem;
  }

  .brand-subtitle {
    font-size: 0.9rem;
  }

  .logo-circle {
    width: 80px;
    height: 80px;
  }

  .logo-circle svg {
    width: 40px;
    height: 40px;
  }

  .brand-features {
    gap: 15px;
  }

  .feature-item {
    font-size: 0.9rem;
  }

  .form-section {
    padding: 30px 20px;
  }

  .form-header {
    margin-bottom: 30px;
  }

  .form-title {
    font-size: 1.5rem;
  }

  .form-options {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .page-footer {
    position: relative;
    margin-top: 20px;
    bottom: auto;
  }
}

@media (max-width: 480px) {
  .brand-section {
    padding: 25px 15px;
  }

  .form-section {
    padding: 25px 15px;
  }

  .form-title {
    font-size: 1.35rem;
  }
}

/* ==================== 打印样式 ==================== */
@media print {
  .background-wrapper,
  .brand-section,
  .page-footer {
    display: none;
  }

  .login-wrapper {
    box-shadow: none;
    border: 1px solid #e5e7eb;
  }
}
</style>
