<template>
  <div v-if="showAuthFix" class="auth-fix-overlay">
    <div class="auth-fix-modal">
      <h3>认证已过期</h3>
      <p>您的登录状态已过期，请重新登录以继续使用系统。</p>
      
      <el-form @submit.prevent="quickLogin" :loading="isLoading">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.yonghu_ming" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input 
            v-model="loginForm.mima" 
            type="password" 
            placeholder="请输入密码"
            @keyup.enter="quickLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="quickLogin" :loading="isLoading">
            重新登录
          </el-button>
          <el-button @click="goToLoginPage">
            前往登录页
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/modules/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()

const showAuthFix = computed(() => {
  // 如果没有token或用户信息，显示修复界面
  return !authStore.isAuthenticated && 
         (localStorage.getItem('access_token') || 
          window.location.pathname !== '/login')
})

const isLoading = ref(false)
const loginForm = ref({
  yonghu_ming: 'admin',
  mima: 'admin123'
})

const quickLogin = async () => {
  if (!loginForm.value.yonghu_ming || !loginForm.value.mima) {
    ElMessage.error('请输入用户名和密码')
    return
  }

  isLoading.value = true
  try {
    const success = await authStore.login(loginForm.value)
    if (success) {
      ElMessage.success('登录成功，正在刷新页面...')
      // 刷新当前页面
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    }
  } catch (error) {
    console.error('快速登录失败:', error)
  } finally {
    isLoading.value = false
  }
}

const goToLoginPage = () => {
  router.push('/login')
}

onMounted(() => {
  // 检查是否需要显示认证修复界面
  console.log('AuthFix mounted, showAuthFix:', showAuthFix.value)
})
</script>

<style scoped>
.auth-fix-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.auth-fix-modal {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  min-width: 400px;
  max-width: 500px;
}

.auth-fix-modal h3 {
  margin-top: 0;
  color: #e74c3c;
  text-align: center;
}

.auth-fix-modal p {
  text-align: center;
  color: #666;
  margin-bottom: 20px;
}
</style>
