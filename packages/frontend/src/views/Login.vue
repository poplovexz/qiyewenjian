<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1 animate-fade-in animate-delay-100"></div>
        <div class="shape shape-2 animate-fade-in animate-delay-200"></div>
        <div class="shape shape-3 animate-fade-in animate-delay-300"></div>
        <div class="shape shape-4 animate-fade-in animate-delay-500"></div>
      </div>
      <div class="gradient-overlay animate-fade-in"></div>
    </div>

    <!-- 登录卡片 -->
    <ModernCard
      variant="glass"
      size="large"
      :elevated="true"
      class="login-card animate-scale-in-bounce"
    >
      <template #header>
        <div class="login-header animate-fade-in-down animate-delay-300">
          <div class="logo-section">
            <div class="logo-icon animate-rotate-in animate-delay-500">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h1 class="login-title">代理记账营运内部系统</h1>
          </div>
          <p class="login-subtitle">欢迎回来，请登录您的账户</p>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="yonghu_ming" class="form-item animate-fade-in-up animate-delay-700">
          <ModernInput
            v-model="loginForm.yonghu_ming"
            label="用户名"
            placeholder="请输入用户名"
            prefix-icon="User"
            :clearable="true"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item prop="mima" class="form-item animate-fade-in-up animate-delay-1000">
          <ModernInput
            v-model="loginForm.mima"
            type="password"
            label="密码"
            placeholder="请输入密码"
            prefix-icon="Lock"
            :clearable="true"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <div class="form-options animate-fade-in-up animate-delay-1000">
          <el-checkbox v-model="rememberMe" class="remember-me">
            记住我
          </el-checkbox>
          <a href="#" class="forgot-password hover-scale">忘记密码？</a>
        </div>

        <el-form-item class="submit-item animate-fade-in-up animate-delay-1000">
          <ModernButton
            variant="primary"
            size="large"
            :loading="isLoading"
            :gradient="true"
            :elevated="true"
            class="login-button w-full hover-glow"
            @click="handleLogin"
          >
            <span v-if="!isLoading">登录</span>
            <span v-else>登录中...</span>
          </ModernButton>
        </el-form-item>
      </el-form>

      <div v-if="error" class="error-message animate-shake animate-fade-in">
        <el-icon class="error-icon"><Warning /></el-icon>
        {{ error }}
      </div>

      <template #footer>
        <div class="login-footer animate-fade-in-up animate-delay-1000">
          <p class="footer-text">
            还没有账户？ 
            <a href="#" class="register-link">联系管理员</a>
          </p>
          <p class="copyright">© 2024 代理记账营运内部系统. All rights reserved.</p>
        </div>
      </template>
    </ModernCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElForm, ElMessage } from 'element-plus'
import { User, Lock, Warning } from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'
import type { LoginRequest } from '@/api/auth'
import ModernCard from '@/components/ui/ModernCard.vue'
import ModernInput from '@/components/ui/ModernInput.vue'
import ModernButton from '@/components/ui/ModernButton.vue'

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
})
</script>

<style scoped>
/* 登录容器 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--primary-gradient);
  opacity: 0.9;
}

.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 10%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 10%;
  right: 20%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 1;
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: var(--primary-gradient);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-lg);
}

.logo-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
}

/* 表单样式 */
.login-form {
  margin-bottom: 1.5rem;
}

.form-item {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

/* 输入框样式由ModernInput组件处理 */

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.remember-me :deep(.el-checkbox__label) {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.forgot-password {
  font-size: 0.875rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.forgot-password:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

/* 提交按钮 */
.submit-item {
  margin-bottom: 0;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  background: var(--primary-gradient);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-md);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.login-button:active {
  transform: translateY(0);
}

/* 错误信息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(245, 101, 101, 0.1);
  border: 1px solid rgba(245, 101, 101, 0.2);
  border-radius: var(--radius-md);
  color: var(--error-color);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.error-icon {
  color: var(--error-color);
}

/* 登录底部样式由ModernCard footer处理 */

.footer-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0 0 1rem 0;
}

.register-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.register-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.copyright {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .login-container {
    padding: 1rem;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
  
  .form-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .logo-icon {
    width: 56px;
    height: 56px;
  }
  
  .logo-icon svg {
    width: 28px;
    height: 28px;
  }
}

/* 深色模式由现代化组件自动处理 */
</style>
